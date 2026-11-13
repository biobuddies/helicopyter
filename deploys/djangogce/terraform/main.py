"""One Django VM; synthesize with python -m helicopyter djangogce."""

from pathlib import Path

from helicopyter import Block, data, provider, resource, string, terraform, var, variable

terraform(required_version='>= 1.4')
terraform.required_providers(google={'source': 'hashicorp/google', 'version': '~> 6.0'})
provider.google(project=var.project, zone=var.zone)

for name, description in {
    'project': 'Existing Google Cloud project with billing and required APIs enabled.',
    'zone': 'Compute zone, for example us-central1-a.',
    'service_account': 'Existing VM service account email; grant access to the environment secret.',
    'repository': 'Public HTTPS Git repository containing the Django application.',
    'revision': 'Full immutable Git commit SHA; change on every deployment.',
    'environment_secret': 'projects/PROJECT/secrets/NAME/versions/NUMBER containing app.env.',
    'wsgi_module': 'Gunicorn application, for example config.wsgi:application.',
    'celery_app': 'Celery application, for example config.',
}.items():
    variable(name)(type=string, description=description)

data.google_compute_image.ubuntu(family='ubuntu-2404-lts-amd64', project='ubuntu-os-cloud')
network = resource.google_compute_network.django(auto_create_subnetworks=True, name='django')
resource.google_compute_firewall.iap(
    name='django-iap-ssh',
    network=network.id,
    source_ranges=['35.235.240.0/20'],
    target_tags=['django'],
    allow=Block('allow')(protocol='tcp', ports=['22']),
)
resource.google_compute_firewall.web(
    name='django-http',
    network=network.id,
    source_ranges=['0.0.0.0/0'],
    target_tags=['django'],
    allow=Block('allow')(protocol='tcp', ports=['80']),
)
address = resource.google_compute_address.django(
    name='django', region=Block('join("-", slice(split("-", var.zone), 0, 2))')
)
# TODO Disaggregate PostgreSQL onto a separately backed-up database service.
# TODO Isolate singleton Celery beat; horizontally scale web and Celery workers independently.
instance = resource.google_compute_instance.django(
    name='django',
    machine_type='e2-standard-2',
    tags=['django'],
    boot_disk=Block('boot_disk')(
        auto_delete=False,
        initialize_params=Block('initialize_params')(
            image=data.google_compute_image.ubuntu.self_link, size=30, type='pd-balanced'
        ),
    ),
    network_interface=Block('network_interface')(
        network=network.id, access_config=Block('access_config')(nat_ip=address.address)
    ),
    service_account=Block('service_account')(
        email=var.service_account, scopes=['https://www.googleapis.com/auth/cloud-platform']
    ),
    metadata={
        'enable-oslogin': 'TRUE',
        'app-repository': var.repository,
        'app-revision': var.revision,
        'app-environment-secret': var.environment_secret,
        'app-wsgi-module': var.wsgi_module,
        'app-celery-app': var.celery_app,
        'user-data': (Path(__file__).parent / 'cloud-init.yaml').read_text().replace('${', '$${'),
    },
    lifecycle=Block('lifecycle')(
        ignore_changes=[Block('boot_disk[0].initialize_params[0].image')], prevent_destroy=True
    ),
)

# cloud-init runs once; this provisioner also deploys metadata changes on the existing VM.
resource.terraform_data.deploy(
    triggers_replace=[
        instance.id,
        Block('sha256(jsonencode(google_compute_instance.django.metadata))'),
    ],
    depends_on=[resource.google_compute_instance.django, resource.google_compute_firewall.iap],
    provisioner=Block('provisioner', 'local-exec')(
        command='bash ../redeploy.bash',
        environment={'PROJECT': var.project, 'ZONE': var.zone, 'INSTANCE': instance.name},
    ),
)
Block('output', 'address')(value=address.address)
