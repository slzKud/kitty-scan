from ping3 import ping
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QStringListModel,QThread,pyqtSignal
import sys,time,json,redis
import ip,oamFactory
from ui.kittyscan import Ui_MainWindow
class RedisThread(QThread):
    sig = pyqtSignal(dict)
    def __init__(self,argument_=True):
        super(RedisThread,self).__init__()
    def run(self):
        import redis
        rc = redis.StrictRedis(host='127.0.0.1', port='6379', db=0, password='')
        ps = rc.pubsub()
        print('已启动redis_f_%s'%(oamFactory.getMAC()))
        ps.subscribe('redis_f_%s'%(oamFactory.getMAC()))
        for item in ps.listen():
            if(item['type']=="message"):
                msg=item['data'].decode("utf-8")	
                jl=json.loads(msg)
                self.sig.emit(jl)
class Thread(QThread):
    sig = pyqtSignal(int,str,int)
    data=0
    def __init__(self,argument_=True):
        self.data=argument_
        print(self.data)
        super(Thread,self).__init__()
    def run(self):
        i1=0
        for i in self.data:
            ret = ping("%s" % i)
            if ret is None:
                r=0
            else:
                r=1
            i1=i1+1
            self.sig.emit(int(i1/len(self.data)*100),'%s'% i,r)    
            time.sleep(1)
        self.sig.emit(100,"",0)
class mwindow(QtWidgets.QMainWindow, Ui_MainWindow):
    r=[]
    livselect=""
    def __init__(self):
        #窗体初始化
        super(mwindow, self).__init__()
        self.setupUi(self)
        self.thread = True
        #事件初始化
        self.pushButton.clicked.connect(self.pushButton_click)
        self.pushButton_2.clicked.connect(self.pushButton2_click)
        self.menu_action.triggered.connect(self.menu_click)
        self.listView.clicked.connect(self.listview_click)
        #共用变量
    def __pushButton_click(self, progress,s1,ret):
        slm=QStringListModel()
        if int(progress)==100:
            slm.setStringList(self.r)
            self.listView.setModel(slm)
            self.pushButton.setEnabled(True)
            self.statusbar.showMessage("IP扫描完成")
            self.progressBar.setProperty("value", 100)
            QtWidgets.QMessageBox.about(self, u'提示', u"IP扫描完成")
            return 0
        if ret==1:
            
            if oamFactory.scanOAMFactoryMode(s1)==1:
                self.r.append(s1)
                self.statusbar.showMessage("IP: %s在线，存在OAM"%(s1))
            else:
                self.statusbar.showMessage("IP: %s在线，不存在OAM"%(s1))
            print(self.r)
        else:
            self.statusbar.showMessage("IP: %s不在线"%(s1))
            
        self.progressBar.setProperty("value", int(progress))
    def pushButton_click(self):
        print('按钮1被点击')
        t=self.lineEdit.text()
        if t.strip(' ')=="":
            QtWidgets.QMessageBox.about(self, u'提示', u"IP地址范围为空")
            return -1
        self.thread = Thread(ip.get_ipaddr_arrayA(t))
        self.thread.sig.connect(self.__pushButton_click)
        self.pushButton.setEnabled(False)
        self.thread.start()
    def listview_click(self,qModelIndex):
        print(self.r[qModelIndex.row()])
        self.livselect=self.r[qModelIndex.row()]
    def pushButton2_click(self):
        print('按钮2被点击')
        if self.livselect=="":
            return -1
        f=oamFactory.getOAMFactoryChannel(self.livselect)
        if f==None:
            return -2
        import redis
        rc = redis.StrictRedis(host='127.0.0.1', port='6379', db=0, password='')
        rc.publish(f,json.dumps({"msg":"helloFactory","sub":'redis_f_%s'%(oamFactory.getMAC())}))
        self.statusbar.showMessage("已发送指令给：%s"%(self.livselect))
    def menu_click(self):
        print('菜单被点击')
        QtWidgets.QMessageBox.about(self, u'关于', u"KittyScan V0.1\n用于设备扫描和发现")
def message(msg):
    print(msg)
    import webbrowser
    webbrowser.open_new("http://www.baidu.com/?devicemac=%s&devicename=%s"%(msg['deviceMAC'],"11111"))
if __name__ == "__main__":
    redis_channel=RedisThread(True)
    redis_channel.sig.connect(message)
    redis_channel.start()
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = mwindow()
    slm=QStringListModel()
    slm.setStringList([])
    MainWindow.listView.setModel(slm)
    MainWindow.progressBar.setProperty("value", 0)
    MainWindow.statusbar.showMessage("待命")
    MainWindow.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint|QtCore.Qt.WindowCloseButtonHint)  
    MainWindow.setFixedSize(MainWindow.width(), MainWindow.height())
    MainWindow.show()
    sys.exit(app.exec_())