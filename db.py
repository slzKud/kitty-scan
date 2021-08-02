import sqlite3,os,random,hashlib,json,sys,time
def printEx(s,f,l):
    s="["+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+":"+ os.path.basename(f) +":"+ str(l)+"]"+str(s)
    fiobj=open("{0}/ota.log".format(os.path.dirname(os.path.realpath(__file__))),"a+")
    fiobj.write(s+'\n')
    fiobj.close
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False
def createDb(path):
    if os.path.exists(path):
        os.remove(path)
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('''CREATE TABLE "var" (
  "var_name" TEXT NOT NULL,
  "var_value" TEXT
);''')
    conn.commit()
    conn.close()
def openDb(path):
    if not os.path.exists(path):
        #printEx("正在创建数据库...",__file__,sys._getframe().f_lineno)
        createDb(path)
        #printEx("创建数据库完成...",__file__,sys._getframe().f_lineno)
    conn = sqlite3.connect(path)
    return conn
def getVar(conn,varName):
    #printEx("获取数据%s..."%(varName),__file__,sys._getframe().f_lineno)
    c = conn.cursor()  
    cursor = c.execute('''SELECT "var_name", "var_value"  from "main"."var" where "var_name"='%s' ''' %(varName))
    r=cursor.fetchall()
    if len(r)>0:
        return r[0][1]
    else:
        return ''
def insertVar(conn,varName,varValue):
    #printEx("插入/更改数据%s:%s..."%(varName,varValue),__file__,sys._getframe().f_lineno)
    c = conn.cursor()
    c1=getVar(conn,varName)
    if len(c1)>0:
        c.execute('''UPDATE "main"."var" SET  "var_value" = '{1}' WHERE "var_name" = '{0}';'''.format(varName,varValue))
    else:
        c.execute('''INSERT INTO "main"."var"("var_name", "var_value") VALUES ('%s', '%s');'''%(varName,varValue))
    conn.commit()
def configJson2dbVar():
    conn=fastOpenDb()
    if os.path.exists('{0}/settings.json'.format(os.path.dirname(os.path.realpath(__file__)))):
        f=open('{0}/settings.json'.format(os.path.dirname(os.path.realpath(__file__))),'r',encoding="utf-8")
        j=f.read()
        j_l=json.loads(j)
        for x in j_l.keys():
            print(x)
            insertVar(conn,x,json.dumps(j_l[x]))
        return True
    else:
        return False
def dbVar2ConfigObj():
    conn=fastOpenDb()
    c = conn.cursor()  
    cursor = c.execute('''SELECT "var_name", "var_value"  from "main"."var" ''')
    r=cursor.fetchall()
    c1={}
    for x in r:
        #print("%s:%s\n"%(x[0],x[1]))
        if "{" not in x[1] or "}" not in x[1]:
            if not is_number(x[1]):
                c1[x[0]]=x[1]
            else:
                c1[x[0]]=eval(x[1])
        else:
            c1[x[0]]=json.loads(x[1])
    #printEx("读取设置完成！",__file__,sys._getframe().f_lineno)
    return c1
def fastOpenDb():
    return openDb('{0}/settings.db'.format(os.path.dirname(os.path.realpath(__file__))))
if __name__ == "__main__":
    openDb('{0}/settings.db'.format(os.path.dirname(os.path.realpath(__file__))))
    print("数据库初始化完成")