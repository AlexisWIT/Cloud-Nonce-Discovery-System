import AWS_Services as aws
import threading
import time
import os
from Settings import Settings
from Messenger import msgThread

def create_user_profile():
    userDir = os.path.join(os.path.expanduser('~'), '.aws')

    if not os.path.exists(userDir):
        os.makedirs(userDir)
        print ("User config dir doesn't exist, creating a new one:")

    else:
        print("User config dir found: ")

    print ("Path: " + userDir)
    
    credentials_file = open(userDir + "\credentials", 'w')
    config_file = open(userDir + "\config", 'w')
    
    credentials_file.write(Settings._AWS_CREDENTIALS)
    config_file.write(Settings._AWS_CONFIG)

def delete_old_report(): # Delete local out-dated report
    try:
        os.remove(Settings._REPORT_FILENAME)
    except:
        print ("No old report need to be deleted")


def main():
    time_out = False
    start_time = time.time()
    create_user_profile()
    delete_old_report()
    
    aws.create_new_bucket()
    aws.create_new_endpoint()
    aws.create_new_security_group()
    aws.create_new_launch_template()
    
    # Create SQS Message Queue and start distributing tasks
    queueUrl = aws.create_new_queue()
    if queueUrl is False:
        queueUrl = aws.get_queue_url_by_name()

    Settings.set_queue_url(Settings, queueUrl)
    thread1 = msgThread(1, "Message_Sender_1", Settings._AWS_SQS_QUEUE_URL, Settings._WORK_PER_PACKAGE, 1, Settings._TOTAL_PACKAGES)
    thread2 = msgThread(2, "Message_Sender_2", Settings._AWS_SQS_QUEUE_URL, Settings._WORK_PER_PACKAGE, 2, Settings._TOTAL_PACKAGES)
    thread1.start()
    thread2.start()

    aws.create_new_instance()
    while aws.download_report() is not True:
        # print("The CND System is still looking for the Golden Nonce.", end = "\r")
        time.sleep(10)
        if (round(time.time()-start_time, 2) >= float(Settings._TIME_DESIRED)):
            print("Time limit reached, shutting down the system...")
            time_out = True
            break
        continue

    thread1.terminate()
    thread2.terminate()

    try:
        file_access = open(Settings._REPORT_FILENAME, 'r')
        for line in file_access:
            print(line)
        file_access.close()
    except IOError as e:
        print ("No report found")
        
    aws.reset_aws_services()
    
if __name__ == "__main__":
    main()