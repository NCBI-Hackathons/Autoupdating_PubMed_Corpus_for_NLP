from settings import *
import os
from subprocess import run, PIPE
import datetime
import resource
from FTPClient import *

class Runner:
    def __init__(self, params):
        # Load everything from the object translated from the JSON file
        self.__dict__ = params

    def run(self):
        self.successed = False
        tries = 0
        while not self.successed and tries < FAIL_LIMIT:
            try:
                destination = ROOT+OUTPUT+self.name+"/"+self.version+"/"

                # Set log files
                stderrf = open(destination+"std.err","wb")
                stdoutf = open(destination+"std.out","wb")
                process = run([self.command,
                              "tools/"+self.name+"/"+self.version+"/"+self.main,
                              "-i"+ROOT+DB,
                              "-o"+destination],
                              stdout=stdoutf,
                              stderr=stderrf,
                              timeout=self.timeout,
                              check=True)
                self.successed = True
            except:
                tries += 1
                pass
            self.lastRun = datetime.datetime.now().strftime("%m-%d-%Y")
            self.pushToFTP()

    def pushToFTP(self):
        output = ROOT+OUTPUT+self.name+"/"+self.version+"/"

        # Push output folder contents
        # 1. Set up FTP
        ftpc = FTPClient(FTP_ADDRESS, FTP_USERNAME, FTP_PASSWORD)
        # 2. Go the the right directory, or create it
        ftpc.cdTree(self.name+"/"+self.version+"/")
        # 3. Upload all files
        for f in os.listdir(output):
            ftpc.upload(output, f)
        # 4. Close session
        ftpc.quit()

        # Delete that content locally
        for f in os.listdir(output):
            fPath = os.path.join(output, f)
            try:
                if os.path.isfile(fPath):
                    os.unlink(fPath)
            except Exception as e:
                print(e)
