import AWS_Services as aws
import threading
import time

class msgThread(threading.Thread):
    def __init__(self, threadId, name, queue_url, work_per_package, first, last):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.name = name
        self.queueUrl = queue_url
        self.work = work_per_package
        self.firstMsgIndex = first
        self.lastMsgIndex = last
        self.exit_flag = False
        
    def run(self):
        i = 0
        startTime = time.time()
        for package_index in range(self.firstMsgIndex, self.lastMsgIndex+1, 2): # 4096 msgs in this case
            result = aws.send_new_message(self.queueUrl, package_index)
            if self.exit_flag:
                print('Thread-%s:' % (self.firstMsgIndex))
                print("Stop sending the computation package")
                break
            if result is False:
                print ("Failed to send message: Package "+ str(package_index))
                break
            else:
                if self.threadId == 2:
                    timeUsed = round(time.time() - startTime, 2)
                    progress = round(round(package_index/self.lastMsgIndex, 4)*100, 2)
                    print ("[{0}%] - Package: {1}, Time Elapsed: {2}".format(progress, package_index, timeUsed), end = "\r")

    def terminate(self):
        self.exit_flag = True

