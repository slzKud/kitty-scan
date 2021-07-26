from ping3 import ping
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QStringListModel,QThread,pyqtSignal
import sys,time,json,redis
import ip
from ui.kittyscan import Ui_MainWindow
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
    def __init__(self):
        #窗体初始化
        super(mwindow, self).__init__()
        self.setupUi(self)
        self.thread = True
        #事件初始化
        self.pushButton.clicked.connect(self.pushButton_click)
        self.pushButton_2.clicked.connect(self.pushButton2_click)
        self.menu_action.triggered.connect(self.menu_click)
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
            self.statusbar.showMessage("IP: %s，存在"%(s1))
            self.r.append(s1)
            print(self.r)
        else:
            self.statusbar.showMessage("IP: %s，不存在"%(s1))
            
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
    def pushButton2_click(self):
        print('按钮2被点击')
        rc = redis.StrictRedis(host='127.0.0.1', port='6379', db=0, password='')
        rc.publish("redis_m_00e26930c510",json.dumps({"msg":"helloFactory","sub":"kittyTest"}))
    def menu_click(self):
        print('菜单被点击')
        QtWidgets.QMessageBox.about(self, u'关于', u"KittyScan V0.1\n用于设备扫描和发现")
if __name__ == "__main__":
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