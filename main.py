from ping3 import ping
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QStringListModel,QThread,pyqtSignal
import sys,time,json,redis,os
import ip,oamFactory,db
from ui.kittyscan import Ui_MainWindow
from ui.redisSettings import Ui_redisSettings
class RedisThread(QThread):
    sig = pyqtSignal(dict)
    def __init__(self,argument_=True):
        super(RedisThread,self).__init__()
    def run(self):
        import redis
        rc = redis.StrictRedis(host=db.getVar(db.fastOpenDb(),"redisIP"), port=db.getVar(db.fastOpenDb(),"redisPort"), db=int(db.getVar(db.fastOpenDb(),"redisDBNo")), password=db.getVar(db.fastOpenDb(),"redisPassword"))
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
class redisSettings(QtWidgets.QDialog,Ui_redisSettings):
    def __init__(self):
        #窗体初始化
        super(redisSettings, self).__init__()
        self.setupUi(self)
        #值设置
        self.lineEdit.setText(db.getVar(db.fastOpenDb(),"redisIP"))
        self.lineEdit_2.setText(db.getVar(db.fastOpenDb(),"redisPort"))
        self.lineEdit_3.setText(db.getVar(db.fastOpenDb(),"redisDBNo"))
        self.lineEdit_4.setText(db.getVar(db.fastOpenDb(),"redisPassword"))
        self.lineEdit_5.setText(db.getVar(db.fastOpenDb(),"redisUrl"))
    def update(self):
        self.lineEdit.setText(db.getVar(db.fastOpenDb(),"redisIP"))
        self.lineEdit_2.setText(db.getVar(db.fastOpenDb(),"redisPort"))
        self.lineEdit_3.setText(db.getVar(db.fastOpenDb(),"redisDBNo"))
        self.lineEdit_4.setText(db.getVar(db.fastOpenDb(),"redisPassword"))
        self.lineEdit_5.setText(db.getVar(db.fastOpenDb(),"redisUrl"))
    def accept(self):
        print('点击OK')
        db.insertVar(db.fastOpenDb(),"redisIP",self.lineEdit.text())
        db.insertVar(db.fastOpenDb(),"redisPort",self.lineEdit_2.text())
        db.insertVar(db.fastOpenDb(),"redisDBNo",self.lineEdit_3.text())
        db.insertVar(db.fastOpenDb(),"redisPassword",self.lineEdit_4.text())
        db.insertVar(db.fastOpenDb(),"redisUrl",self.lineEdit_5.text())
        QtWidgets.QMessageBox.about(self, u'提示', u"数据库设置完成！")
        return super().accept()
    def reject(self):
        print('点击Cancel')
        return super().reject()

class mwindow(QtWidgets.QMainWindow, Ui_MainWindow):
    r=[]
    livselect=""
    w2=0
    def __init__(self):
        #窗体初始化
        super(mwindow, self).__init__()
        self.setupUi(self)
        self.thread = True
        self.w2=redisSettings()
        #事件初始化
        self.pushButton.clicked.connect(self.pushButton_click)
        self.pushButton_2.clicked.connect(self.pushButton2_click)
        self.menu_action.triggered.connect(self.menu_click)
        self.menu_Redis_action.triggered.connect(self.menu_Redis_click)
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
        rc = redis.StrictRedis(host=db.getVar(db.fastOpenDb(),"redisIP"), port=db.getVar(db.fastOpenDb(),"redisPort"), db=int(db.getVar(db.fastOpenDb(),"redisDBNo")), password=db.getVar(db.fastOpenDb(),"redisPassword"))
        rc.publish(f,json.dumps({"msg":"helloFactory","sub":'redis_f_%s'%(oamFactory.getMAC())}))
        self.statusbar.showMessage("已发送指令给：%s"%(self.livselect))
    def menu_click(self):
        print('菜单被点击')
        QtWidgets.QMessageBox.about(self, u'关于', u"KittyScan V0.1\n用于设备扫描和发现")
    def menu_Redis_click(self):
        print('菜单2被点击')
        self.w2.update()
        self.w2.show()
def message(msg):
    print(msg)
    import webbrowser
    webbrowser.open_new(db.getVar(db.fastOpenDb(),"redisUrl").format(msg['deviceMAC'],"11111"))
if __name__ == "__main__":
    if not os.path.exists('{0}/settings.db'.format(os.path.dirname(os.path.realpath(__file__)))):
        print('数据库不存在，打开设置页面')
        app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QMessageBox.about(None, u'提示', u"当前数据库不存在,即将打开设置页面重新创建。")
        w3=redisSettings()
        w3.update()
        w3.show()
        sys.exit(app.exec_())
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