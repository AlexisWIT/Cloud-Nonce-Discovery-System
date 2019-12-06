
content = """#!/bin/bash
yum update -y 
yum install python36 -y

mkdir /home/ec2-user/.aws
touch /home/ec2-user/.aws/credentials
touch /home/ec2-user/.aws/config

echo '%(CREDENTIALS)s' > /home/ec2-user/.aws/credentials

echo '%(CONFIG)s' > /home/ec2-user/.aws/credentials

mkdir /home/ec2-user/venv
cd /home/ec2-user/venv

virtualenv -p /usr/bin/python36 python36

source /home/ec2-user/venv/python36/bin/activate

pip3 install boto3

python -c "import time
import datetime
import boto3
import logging
import urllib.request
from botocore.exceptions import ClientError
from hashlib import sha256

_TOTAL_VM = '%(TOTAL_VM)s'
_DIFFICUITY = '%(DIFFICUITY)s'
_RAW_DATA = '%(RAW_DATA)s'
_START_DATETIME = datetime.datetime.now()
_START_TIME = time.time()
_SQS_QUEUE_URL = '%(SQS_QUEUE_URL)s'
_S3_BUCKET_NAME = '%(S3_BUCKET_NAME)s'
_AWS_REGION = '%(AWS_REGION)s'
_REPORT_FILENAME = '%(REPORT_FILENAME)s'
_ACCESS_KEY = '%(ACCESS_KEY)s'
_SECRET_KEY = '%(SECRET_KEY)s'
_SESSION_TOKEN = '%(SESSION_TOKEN)s'

class Block:

    def __init__(self, data, vm, initNonce, endNonce, handle):
        self.timeStamp = _START_DATETIME
        self.data = data                # COMSM0010cloud
        self.initHash2 = self.getHash2()
        self.nonce = initNonce          # Depend on VM
        self.goldenHash2 = self.getHash2()
        self.nonce_end = endNonce
        self.start_time = _START_TIME
        self.receiptHandle = handle
        #self.vm = vm                    # Number of VM used

    def getHash2(self, nonce=None):
        plain_data = str(self.data) + str(nonce)
        hash1 = sha256(plain_data.encode('utf-8')).hexdigest()
        hash2 = sha256(hash1.encode('utf-8')).hexdigest()
        return hash2

    def findNonce(self): #39
        while(self.goldenHash2[0:int(_DIFFICUITY)] != str(0).zfill(int(_DIFFICUITY)) and int(self.nonce) <= int(self.nonce_end)):
            self.nonce += 1
            self.goldenHash2 = self.getHash2(int(self.nonce))

        if (self.goldenHash2[0:int(_DIFFICUITY)] != str(0).zfill(int(_DIFFICUITY))):
            print('No nonce found from current package')
            return False
        else:
            print('Golden nonce found')
            return True
    
    def get_vm_id(self):
        instanceid = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read().decode()
        
    # For printing result in plain text
    def __str__(self): #54 
        line_1 = 'Start/End Time: '+str(self.timeStamp)+' - '+str(datetime.datetime.now())+'\\n'
        timeUsed = round(time.time()-float(self.start_time), 2)
        line_2 = 'Time Used:      '+str(timeUsed)+'s\\n'
        line_3 = 'Block Data:     '+str(self.data)+'\\n'
        line_4 = 'Initial Hash^2: '+str(self.initHash2)+'\\n'
        line_5 = 'Golden Nonce:   '+str(self.nonce)+'\\n'
        line_6 = 'Golden Hash^2:  '+str(self.goldenHash2)+'\\n'
        line_7 = 'Difficuity:     '+str(_DIFFICUITY)+'\\n'
        line_8 = 'Found by VM:    '+str(self.get_vm_id())+'\\n'
        result = line_1 + line_2 + line_3 + line_4 + line_5 + line_6 + line_7 + line_8
        return result

def receive_new_message():
    try:
        sqs_client = boto3.client(
            'sqs', 
            region_name=_AWS_REGION,
            aws_access_key_id=_ACCESS_KEY, 
            aws_secret_access_key=_SECRET_KEY, 
            aws_session_token=_SESSION_TOKEN
            )
        response = sqs_client.receive_message(
            QueueUrl = _SQS_QUEUE_URL,
            AttributeNames = ['All'],
            MessageAttributeNames = ['Start_Number', 'End_Number', 'Total'],
            MaxNumberOfMessages=1
        )

        message_body = str(response['Messages'][0]['Body'])
        start_nonce = int(response['Messages'][0]['MessageAttributes']['Start_Number']['StringValue'])
        end_nonce = int(response['Messages'][0]['MessageAttributes']['End_Number']['StringValue'])
        total_num = int(response['Messages'][0]['MessageAttributes']['Total']['StringValue'])
        receipt_handle = str(response['Messages'][0]['ReceiptHandle'])

        # _START_TIME = time.time()
        # _START_DATETIME = datetime.datetime.now()

        block = Block(_RAW_DATA, _TOTAL_VM, start_nonce, end_nonce, receipt_handle)

    except ClientError as e:
        logging.error(e)
        return False
    return block

def delete_processed_messsage(receipt_Handle_Id):
    try:
        sqs_client = boto3.client(
            'sqs',  
            region_name=_AWS_REGION,
            aws_access_key_id=_ACCESS_KEY, 
            aws_secret_access_key=_SECRET_KEY, 
            aws_session_token=_SESSION_TOKEN
            )
        response = sqs_client.delete_message(
            QueueUrl = _SQS_QUEUE_URL,
            ReceiptHandle = receipt_Handle_Id
        )
    
    except ClientError as e:
        logging.error(e)
        return False
    return True

def create_report(content): #121
    report_file = open(_REPORT_FILENAME, 'w')
    report_file.write(str(content))

def upload_report():
    try:
        s3_client = boto3.resource(
            's3', 
            aws_access_key_id=_ACCESS_KEY, 
            aws_secret_access_key=_SECRET_KEY, 
            aws_session_token=_SESSION_TOKEN
            )
        s3_client.meta.client.upload_file(
            _REPORT_FILENAME,   # The path to the file to upload
            _S3_BUCKET_NAME,    # The name of the bucket to upload to
            _REPORT_FILENAME    # The name of the key to upload to.
            )

    except ClientError as e:
        logging.error(e)
        return False
    return True

while True:
    workBlock = receive_new_message()
    if (workBlock.findNonce()) is True:
        print(workBlock)
        create_report(workBlock)
        upload_report()
        break

    delete_processed_messsage(workBlock.receiptHandle)
"
"""