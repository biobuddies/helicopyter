"""
Mostly minimal Django deployment to AWS EC2

The one slight sophistication is support for low-downtime "blue-green" deployments.
"""

from cdktf_cdktf_provider_aws.instance import Instance
from cdktf_cdktf_provider_aws.internet_gateway import InternetGateway
from cdktf_cdktf_provider_aws.lb import Lb
from cdktf_cdktf_provider_aws.lb_listener import LbListener, LbListenerDefaultAction
from cdktf_cdktf_provider_aws.lb_target_group import LbTargetGroup
from cdktf_cdktf_provider_aws.lb_target_group_attachment import LbTargetGroupAttachment
from cdktf_cdktf_provider_aws.route_table import RouteTable, RouteTableRoute
from cdktf_cdktf_provider_aws.route_table_association import RouteTableAssociation
from cdktf_cdktf_provider_aws.subnet import Subnet
from cdktf_cdktf_provider_aws.vpc import Vpc

from helicopyter import HeliStack


def synth(stack: HeliStack):
    stack.provide('aws', region='us-west-2')

    vpc = stack.push(Vpc, 'this', cidr_block='10.0.0.0/16')
    stack.push(Subnet, 'private', vpc_id=vpc.id, cidr_block='10.0.1.0/24', tags={'Name': 'private'})
    subnet = stack.push(
        Subnet, 'public', vpc_id=vpc.id, cidr_block='10.0.2.0/24', tags={'Name': 'public'}
    )
    stack.push(
        RouteTableAssociation,
        'this',
        subnet_id=subnet.id,
        route_table_id=stack.push(
            RouteTable,
            'this',
            vpc_id=vpc.id,
            route=[
                RouteTableRoute(
                    cidr_block='0.0.0.0/0',
                    gateway_id=stack.push(InternetGateway, 'this', vpc_id=vpc.id).id,
                )
            ],
        ).id,
    )

    target_group = stack.push(LbTargetGroup, 'this', port=80, protocol='HTTP', vpc_id=vpc.id)

    # Do we need a NAT for connectivity to apt package servers, uv, GitHub?
    for role, count in {'beat': 1, 'web': 2, 'worker': 1}.items():
        for idnt in range(count):
            instance = stack.push(
                Instance,
                f'{role}-{idnt}',
                # 24.04 Noble Numbat in us-west-2 from https://cloud-images.ubuntu.com/locator/ec2/
                ami='ami-0026a04369a3093cc',
                instance_type='t2.micro',
                # TODO userdata that
                # * fetches git
                # * bootstraps uv
                # * runs uv venv and uv pip install -r requirements.txt
            )
            if role == 'web':
                stack.push(
                    LbTargetGroupAttachment,
                    f'{role}-{idnt}',
                    target_id=instance.id,
                    target_group_arn=target_group.arn,
                    port=8000,
                )

    stack.push(
        LbListener,
        'this',
        load_balancer_arn=stack.push(
            Lb,
            'this',
            internal=False,
            load_balancer_type='application',
            # Probably need to create and use security groups
            subnets=[subnet.id],
        ).arn,
        port=80,
        protocol='HTTP',
        default_action=[LbListenerDefaultAction(type='forward', target_group_arn=target_group.arn)],
    )

    # TODO RDS
