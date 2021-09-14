import threading
# 封装好的线程管理类
class ThreadCli(threading.Thread):
    def __init__(self,func,args,name=''):
        threading.Thread.__init__(self)
        self.func = func
        self.name = name
        self.args = args

    def run(self):
        self.res = self.func(*self.args)

    def getResult(self):
        return self.res