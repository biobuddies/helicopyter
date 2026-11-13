# Django on one Google Cloud VM

This Python Syntax for Terraform example puts PostgreSQL, Redis, Gunicorn, Celery workers,
one Celery beat, and nginx on Ubuntu 24.04. It assumes the deployed repository contains
`manage.py`, committed migrations, `requirements.txt`, and the biobuddies/measles mise
configuration, including pinned uv and Python versions. Gunicorn, Django, Celery, the PostgreSQL
driver, and Redis transport must come from that requirements file; nothing installs Gunicorn
separately. Development packages mirror `DEBS` in `.biobuddies/includes.bash`.

Use a public HTTPS Git repository and a full commit SHA. Private checkout credentials are a
followup; do not put a token in the repository URL or VM metadata. App code and mise configuration
are trusted and execute as `django`. The example deliberately disables mise hooks, whose measles
postinstall recompiles requirements; `mise install`, `uv venv`, and `uv pip sync requirements.txt`
install the committed dependencies. If present, `package-lock.json` supplies Node dependencies.
Add an app-specific asset build before `collectstatic` when needed.

## Prerequisites and permissions

Prepare these together before applying. Infrastructure uses Application Default Credentials;
the local deployment provisioner also requires `gcloud`, its own authenticated identity, Bash,
and the IAP SSH transport dependencies. For local work, run both `gcloud auth login` and
`gcloud auth application-default login`, selecting the intended project and identities. CI should
use workload identity federation rather than service account keys.

| Identity or dependency | Required access/setup |
| --- | --- |
| Project bootstrap administrator | Billing enabled; enable `compute.googleapis.com`, `iam.googleapis.com`, `iap.googleapis.com`, `oslogin.googleapis.com`, and `secretmanager.googleapis.com`. Enabling APIs requires `roles/serviceusage.serviceUsageAdmin`; API consumers may need `roles/serviceusage.serviceUsageConsumer` on their quota project. |
| Terraform identity | `roles/compute.instanceAdmin.v1`, `roles/compute.networkAdmin`, and `roles/compute.securityAdmin` on this project for VM/disk/address, network, and firewall lifecycle; `roles/iam.serviceAccountUser` on the selected VM service account to attach it. Image lookup requires Compute image read access. These are convenient predefined roles; narrow them for production. |
| gcloud deployment/operator identity | `roles/iap.tunnelResourceAccessor`, `roles/compute.osAdminLogin` for SSH with sudo, Compute instance/project read access, and `roles/iam.serviceAccountUser` on the attached service account. Users outside the organization may also need `roles/compute.osLoginExternalUser` at organization scope. IAM conditions and organization policies must permit this instance and TCP 22. |
| VM service account | An existing dedicated service account with `roles/secretmanager.secretAccessor` on the single app environment secret. The VM uses the metadata server and `cloud-platform` OAuth scope; it needs no Terraform or project administration permissions. |
| Secret administrator | Create the secret/version and grant the VM identity access before apply; Terraform neither provisions nor reads the secret payload. |
| Network and capacity | Regional external IPv4 and VM/disk quota; organization policies permitting external IPs, OS Login, and this service account. Egress DNS/HTTPS to GitHub, mise/tool download hosts, Python/npm registries and Secret Manager, plus Ubuntu package repositories. IAP reaches port 22; public ingress only reaches nginx on 80. PostgreSQL, Redis and Gunicorn remain local. |
| State operator | This example uses local state; protect it and the generated metadata. For shared state, configure a locking backend and grant its identity read/write/lock access separately. Never run concurrent applies. |

TODO Automate a single preflight that aggregates missing API enablement, effective IAM permissions
for both deployer identities and the VM identity (including conditional grants/deny policies), secret
version existence/access, OS Login/sudo, IAP SSH, egress, organization policies and regional quota.
Run it before initial deployment and every (re)start, report all failures together, and exit before
stopping processes. Aim to get (re)start right the first time, avoiding serial permission discovery.
The current SSH retry loop handles VM readiness; it does not implement that preflight.

Create a numbered Secret Manager version containing a trusted environment file. Use simple
`KEY=value` assignments with single-quoted literal values when necessary; the file is consumed
by both Bash and systemd. Avoid shell expansion, command substitution, `export`, multiline values,
and `%` specifiers. It executes as the app user when sourced. Include your settings' actual names,
for example, if the app reads these variables:

```sh
DJANGO_SETTINGS_MODULE=config.settings
SECRET_KEY='replace-with-a-generated-secret'
DEBUG=False
ALLOWED_HOSTS=django.example.com
DATABASE_URL='postgresql:///django?host=/var/run/postgresql'
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
STATIC_ROOT=/opt/django/static
```

Configure Django to consume these values, connect to the local `django` database as OS user
`django` using PostgreSQL peer authentication, and collect static assets into `/opt/django/static`.
Do not rely on a SQLite development default. Add mail/storage/API credentials the app needs to
the same secret. Rotation deploys a new numbered version by changing `environment_secret`.

## Deploy and redeploy

From the Helicopyter checkout, synthesize and validate:

```sh
python -m helicopyter djangogce --format_with terraform
terraform -chdir=deploys/djangogce/terraform init
terraform -chdir=deploys/djangogce/terraform validate
```

Create an ignored `deploys/djangogce/terraform/example.tfvars` with your values:

```hcl
project            = "your-project"
zone               = "us-central1-a"
service_account    = "django@your-project.iam.gserviceaccount.com"
repository         = "https://github.com/your-org/your-django-app.git"
revision           = "0123456789abcdef0123456789abcdef01234567"
environment_secret = "projects/your-project/secrets/django-environment/versions/1"
wsgi_module        = "config.wsgi:application"
celery_app         = "config"
```

```sh
terraform -chdir=deploys/djangogce/terraform plan -var-file=example.tfvars -out=deployment.plan
terraform -chdir=deploys/djangogce/terraform apply deployment.plan
```

Change `revision` for each release, then plan/apply again. Metadata changes trigger an IAP SSH
invocation of `django-deploy.service` on the existing VM. Cloud-init handles first boot;
the enabled deployment service handles subsequent boots. The SSH provisioner waits for cloud-init
and propagates deployment failure to Terraform. First creation runs the idempotent deployment twice.
A no-change apply does nothing; force a retry with `-replace=terraform_data.deploy` when needed.

Each deployment stops web/worker/beat, fetches the selected code and secret, installs dependencies,
runs deployment checks, **`manage.py migrate --noinput`**, then `collectstatic`, before restarting
all three processes. Only the deployment service is enabled at boot, so failed migrations leave
application processes stopped. systemd restarts crashed processes without rerunning migrations;
an explicit deployment or VM boot always migrates. This single-VM approach has deployment downtime.
Create and review migrations in development; production never runs `makemigrations`.

Inspect `sudo cloud-init status --long`, `/var/log/cloud-init-output.log`,
`sudo journalctl -u django-deploy -u django-web -u django-worker -u django-beat`, and
`sudo systemctl status django-web django-worker django-beat`. After repair, restart
`django-deploy.service`; never restart application processes to bypass failed migrations.
Terraform checks service state, not an application HTTP readiness endpoint.

The external IP is stable. HTTP is a bootstrap example: add TLS before serving credentials or user
traffic. Existing Cloudflare `jam()` in `helicopyter/cloudflare.py` demonstrates provider and routing
conventions, but serves Workers assets. Do not point a JAM Worker route at this Django hostname.
For this VM, use an A record to the output address and either configure nginx origin TLS with
Cloudflare Full (strict), or add a Cloudflare Tunnel and restrict public origin ingress. Match
`ALLOWED_HOSTS`, CSRF origins and proxy settings to the chosen hostname and TLS termination.

TODO Disaggregate PostgreSQL, add scheduled backups and tested restores, and move durable app
media off the boot disk. `prevent_destroy` blocks VM replacement and `auto_delete=false` retains
the disk, but neither replaces backups; intentional replacement needs a disk reattachment plan.
Cloud-init edits affect only newly initialized VMs; update existing host files explicitly.
New image-family releases do not replace this database-bearing VM; plan OS upgrades explicitly.
TODO Disaggregate singleton Celery beat, then horizontally scale web and Celery workers separately
behind a load balancer with shared database, broker, static/media storage and a separate migration
job. Preserve one beat scheduler. Keep migrations compatible with overlapping app versions.
Resource names are fixed: use one state/workspace for this example, not per-branch previews.
