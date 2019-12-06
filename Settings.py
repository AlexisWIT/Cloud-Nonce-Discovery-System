
class Settings:

    # Security and Authentication settings
    _AWS_KEY_ID         = "<Key ID Here>"                   # Your AWS Key ID
    _AWS_SECRET_KEY     = "<Secret Key Here>"               # Your AWS Secret Key
    _AWS_SESSSION_TOKEN = ""                                # If you have Permanent Keys. leave this blank
    
    _AWS_CREDENTIALS = ("[default]"+"\n"
                    "aws_access_key_id="+_AWS_KEY_ID+"\n"
                    "aws_secret_access_key="+_AWS_SECRET_KEY+"\n"
                    "aws_session_token="+_AWS_SESSSION_TOKEN)

    # Other settings
    _AWS_OUTPUT_TYPE = "json"
    _AWS_REGION = "us-east-1"
    _AWS_CONFIG = ("[default]"+"\n"
                   "output="+_AWS_OUTPUT_TYPE+"\n"
                   "region="+_AWS_REGION)

    # AWS Services settings
    _AWS_DEFAULT_VPC_ID               = "vpc-88257cf2"             # Check this in VPC Section      EDU: vpc-b5beefcf Personal: vpc-88257cf2
    _AWS_DEFAULT_ROUTETABLE_ID        = "rtb-6365c11d"             # Check this in VPC Section      EDU: rtb-af518dd1 Personal: rtb-6365c11d
    _AWS_S3_BUCKET_NAME               = "bucket-yt15482"           # Better change to a new one
    _AWS_SQS_QUEUE_NAME               = "Task-Publisher.fifo"
    _AWS_SQS_QUEUE_URL                = ""                         # Please leave this blank
    _AWS_INSTANCE_IMAGE_ID            = "ami-00eb20669e0990cb4"
    _AWS_INSTANCE_TYPE                = "t2.micro"
    #_AWS_INSTANCE_KEYPAIR_NAME       = ""                  # Uncomment this if you want to use SSH Login and have your keypair ready
    _AWS_INSTANCE_TEMPLATE_NAME       = "CND_VM_Template"
    _AWS_INSTANCE_SHUTDOWN_BEHAVIOUR  = "terminate"
    _AWS_INSTANCE_SECURITY_GROUP_NAME = "Security_Group_1"

    # User task settings
    _TOTAL_VM         = 1                                   # Number of Instance to be launched
    _TASK_DIFFICUITY  = 7                                   # Diffculty
    _RAW_DATA         = "COMSM0010cloud"
    _WORK_IN_TOTAL    = 2**32                               # Total: 4,294,967,296 (2^32)
    _WORK_PER_PACKAGE = 2**20                               # Computation Task per Package: 1,048,576 (2^20)
    _TOTAL_PACKAGES   = _WORK_IN_TOTAL//_WORK_PER_PACKAGE   # 4096 packages in this case by default
    _TIME_DESIRED     = 60*30                               # Timeout in seconds - default is 30 minutes (1800 seconds)
    _REPORT_FILENAME  = "report.txt"

    def set_total_vm(self, number):
            self._TOTAL_VM = number

    def set_desired_time(self, time_minute):
        self._TIME_DESIRED = time_minute*60

    def set_cost_limit(self, cost_per_hour):
        self._TOTAL_VM = cost_per_hour/0.0116

    def set_queue_url(self, queue_url):
        self._AWS_SQS_QUEUE_URL = queue_url
