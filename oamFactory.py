import requests,json,subprocess,platform
def scanOAMFactoryMode(ip):
    try:
        r=requests.get("http://%s:3852/LoraApi/Factory/Hello"%(ip))
        if r.status_code==200:
            if "{" in r.text and "}" in r.text:
                print(r.text)
                j=json.loads(r.text)
                if j['result']==0:
                    return 1
                else:
                    return 0
            else:
                return -1
        else:
            return -2
    except:
        return -2
def getOAMFactoryChannel(ip):
    try:
        r=requests.get("http://%s:3852/LoraApi/Factory/Hello"%(ip))
        if r.status_code==200:
            if "{" in r.text and "}" in r.text:
                print(r.text)
                j=json.loads(r.text)
                if j['result']==0:
                    return j['redis_channel']
                else:
                    return None
            else:
                return None
        else:
            return None
    except:
        return None
def isLinux():
    if platform.system().lower() == 'windows':
        return False
    elif platform.system().lower() == 'linux':
        return True
def execCmd(cmd):
    p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)  
    out,err = p.communicate()  
    return out.decode()
def getMAC():
    if isLinux():
        mac=execCmd("cat /sys/class/net/eth0/address")
        mac=mac.replace(":","").lower()
    else:
        import uuid
        node = uuid.getnode()
        mac = uuid.UUID(int = node).hex[-12:]
        mac=mac.replace("-","").lower()
    return mac
