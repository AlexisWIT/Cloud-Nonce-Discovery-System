import os
import datetime
import time
import boto3
import logging
from botocore.exceptions import ClientError
from Settings import Settings
from CND_Script import content as Bash_Script_Content

# Create a new S3 Bucket
def create_new_bucket():
    try: 
        s3_client = boto3.client('s3')
        response = s3_client.create_bucket(
            Bucket = Settings._AWS_S3_BUCKET_NAME
            )

        print(f'Bucket {response["Location"]} created')
    except ClientError as e:
        logging.error(e)
        return False
    return True

# Create a new VPC Endpoint
def create_new_endpoint():
    try:
        ec2_client = boto3.client('ec2', Settings._AWS_REGION)
        response = ec2_client.create_vpc_endpoint(
            DryRun = False,
            VpcEndpointType = 'Gateway',
            VpcId = Settings._AWS_DEFAULT_VPC_ID,
            ServiceName = 'com.amazonaws.%s.s3' % (Settings._AWS_REGION),
            PolicyDocument = '{"Statement": [{"Action": "*","Effect": "Allow","Resource": "*","Principal": "*"}]}',
            RouteTableIds = [Settings._AWS_DEFAULT_ROUTETABLE_ID]
            #ClientToken=''
            )

        print(f'Endpoint {response["VpcEndpoint"]["VpcEndpointId"]} created in VPC {response["VpcEndpoint"]["VpcId"]}')

    except ClientError as e:
        logging.error(e)
        return False
    return True

# Create a new Security Group
def create_new_security_group():
    try:
        ec2_client = boto3.client('ec2', Settings._AWS_REGION)
        response = ec2_client.create_security_group(
            Description = 'Security Group for CND',
            GroupName = Settings._AWS_INSTANCE_SECURITY_GROUP_NAME,
            VpcId = Settings._AWS_DEFAULT_VPC_ID,
            DryRun = False
        )

        securityGroupId = response['GroupId']
        print('Security Group [%s] Created' % (securityGroupId))

        ec2_client.authorize_security_group_ingress(
            GroupId = securityGroupId,
            IpPermissions = [
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }
            ]
        )
    except ClientError as e:
        logging.error(e)
        return False
    return True

def delete_all_security_groups():
    try:
        ec2_client = boto3.client('ec2', Settings._AWS_REGION)
        ec2_client.delete_security_group(
            GroupName = Settings._AWS_INSTANCE_SECURITY_GROUP_NAME
        )

    except ClientError as e:
        logging.error(e)
        return False
    return True

# Create a new Launch Template
def create_new_launch_template():
    try:
        ec2_client = boto3.client('ec2', Settings._AWS_REGION)
        response = ec2_client.create_launch_template(
            DryRun = False,
            LaunchTemplateName = Settings._AWS_INSTANCE_TEMPLATE_NAME,
            VersionDescription = 'Initial',
            LaunchTemplateData={
                'ImageId': Settings._AWS_INSTANCE_IMAGE_ID,
                'InstanceType': Settings._AWS_INSTANCE_TYPE,
                #'KeyName': Settings._AWS_INSTANCE_KEYPAIR_NAME,
                'Monitoring': {
                    'Enabled': False
                },
                'InstanceInitiatedShutdownBehavior': Settings._AWS_INSTANCE_SHUTDOWN_BEHAVIOUR,
                #'UserData': 'string',
                'TagSpecifications': [
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': 'CND_Server'
                            },
                        ]
                    },
                ],
                'SecurityGroups': [
                    Settings._AWS_INSTANCE_SECURITY_GROUP_NAME,
                ]
            },
            TagSpecifications=[
                {
                    'ResourceType': 'launch-template',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'CND_Server_Template'
                        },
                    ]
                },
            ]
        )
        print(f'Launch Template - {response["LaunchTemplate"]["LaunchTemplateName"]} ({response["LaunchTemplate"]["LaunchTemplateId"]}) created')

    except ClientError as e:
        logging.error(e)
        return False
    return True

def delete_all_launch_tamplates():
    try:
        ec2_client = boto3.client('ec2', Settings._AWS_REGION)
        response = ec2_client.delete_launch_template(
            LaunchTemplateName = Settings._AWS_INSTANCE_TEMPLATE_NAME
        )

    except ClientError as e:
        logging.error(e)
        return False
    return True

# Create a new EC2 instance
def create_new_instance():
    try:
        ec2_client = boto3.client('ec2', Settings._AWS_REGION)
        USER_DATA = Bash_Script_Content % {
            'TOTAL_VM': Settings._TOTAL_VM,
            'DIFFICUITY': Settings._TASK_DIFFICUITY,
            'RAW_DATA': Settings._RAW_DATA,
            'CREDENTIALS': Settings._AWS_CREDENTIALS,
            'CONFIG': Settings._AWS_CONFIG,
            'SQS_QUEUE_URL': Settings._AWS_SQS_QUEUE_URL,
            'S3_BUCKET_NAME': Settings._AWS_S3_BUCKET_NAME,
            'AWS_REGION': Settings._AWS_REGION,
            'REPORT_FILENAME': Settings._REPORT_FILENAME,
            'ACCESS_KEY': Settings._AWS_KEY_ID,
            'SECRET_KEY': Settings._AWS_SECRET_KEY,
            'SESSION_TOKEN': Settings._AWS_SESSSION_TOKEN
        }
        response = ec2_client.run_instances(
            MaxCount = Settings._TOTAL_VM,
            MinCount = Settings._TOTAL_VM,
            UserData = USER_DATA,
            #ClientToken='',
            LaunchTemplate = {
                'LaunchTemplateName': Settings._AWS_INSTANCE_TEMPLATE_NAME
                #'Version': 'Default'
            },
            DryRun = False,
        )

        for i in range (0, Settings._TOTAL_VM):
            print (f'Instance {response["Instances"][i]["InstanceId"]} created')
        
        print (f'{Settings._TOTAL_VM} instances in total created')

    except ClientError as e:
        logging.error(e)
        return False
    return True

def terminate_all_instances():
    try:
        ec2_client = boto3.client('ec2', Settings._AWS_REGION)
        ec2_resources = boto3.resource('ec2', Settings._AWS_REGION)
        for instance in ec2_resources.instances.all():
            if instance.state != "terminated" and instance.state != "shutting-down":
                response = ec2_client.terminate_instances(
                    InstanceIds = [instance.id]
                )

        print("All active instances are terminated")  
    except ClientError as e:
        logging.error(e)
        return False
    return True     

# Create new SQS queue
def create_new_queue():
    try:
        sqs_client = boto3.client('sqs', Settings._AWS_REGION)
        response = sqs_client.create_queue(
            QueueName = Settings._AWS_SQS_QUEUE_NAME,
            Attributes = {
                'FifoQueue': 'true',
                'ContentBasedDeduplication': 'true'
            },
            tags = {
                'priority': '1',
                'time_created': str(datetime.datetime.now())
            }
        )

        print(f'Queue {response["QueueUrl"]} created')

    except ClientError as e:
        logging.error(e)
        return False
    return response["QueueUrl"]

def get_queue_url_by_name():
    try:
        sqs_client = boto3.client('sqs', Settings._AWS_REGION)
        response = sqs_client.get_queue_url(
            QueueName = Settings._AWS_SQS_QUEUE_NAME
        )

        print(f'Queue {response["QueueUrl"]} obtained')
    except ClientError as e:
        logging.error(e)
        return False
    return response["QueueUrl"]

def delete_all_queues():
    try:
        sqs_client = boto3.client('sqs', Settings._AWS_REGION)
        response = sqs_client.delete_queue(
            QueueUrl = Settings._AWS_SQS_QUEUE_URL
        )

    except ClientError as e:
        logging.error(e)
        return False
    return True

# Create and send SQS messages
def send_new_message(queue_url, computation_pack_index):
    try:
        sqs_client = boto3.client('sqs', Settings._AWS_REGION)
        start_Nonce = str((computation_pack_index-1)*Settings._WORK_PER_PACKAGE)
        end_Nonce = str(int(start_Nonce)+Settings._WORK_PER_PACKAGE-1)
        response = sqs_client.send_message(
            QueueUrl = queue_url,
            MessageBody = 'Computation Package [%s]' % (computation_pack_index),
            MessageAttributes={
                'Start_Number': {
                    'StringValue': start_Nonce,
                    'DataType': 'String'
                },
                'End_Number': {
                    'StringValue': end_Nonce,
                    'DataType': 'String'
                },
                'Total': {
                    'StringValue': str(Settings._WORK_PER_PACKAGE),
                    'DataType': 'String'
                }
            },
            MessageGroupId = 'MyMessageGroupId%s' % (computation_pack_index)
        )

        #if response is not None:
        #    logging.basicConfig(
        #        level = logging.DEBUG,
        #        format = '%(levelname)s: %(asctime)s: %(message)s')
        #    logging.info(
        #        f'Message sent - Seq_Num: {response["SequenceNumber"]}, ID: {response["MessageId"]}'
        #        )

    except ClientError as e:
        logging.error(e)
        return False
    return True

# Doenload the final report
def download_report():
    try:
        s3_resource = boto3.resource('s3')
        s3_resource.meta.client.download_file(
            Settings._AWS_S3_BUCKET_NAME,   # The name of the bucket to download from.
            Settings._REPORT_FILENAME,      # The name of the key to download from.
            Settings._REPORT_FILENAME       # The path to the file to download to.
            )

    except ClientError as e:
        #logging.error(e)
        return False
    return True

def delete_report_file(): # Delete report in S3 Bucket
    try:
        s3_resource = boto3.resource('s3')
        s3_resource.Object(Settings._AWS_S3_BUCKET_NAME, Settings._REPORT_FILENAME).delete()

    except ClientError as e:
        #logging.error(e)
        return False
    return True

def reset_aws_services():
    terminate_all_instances()
    delete_all_queues()
    delete_all_launch_tamplates()
    delete_report_file()
    #delete_all_security_groups()

