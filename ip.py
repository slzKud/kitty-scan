import re
def check_ip(ip):
    r=re.compile(r'^([1-9]\d?|1\d{2}|2[0-4]\d|25[0-5])(\.([1-9]?\d|1\d{2}|2[0-4]\d|25[0-5])){3}')
    matchObj=r.match(ip)
    if matchObj:
        return True
    else:
        return False
def get_startNendIP(ipstr):
    ipstr1=str(ipstr).strip(' ')
    ipstr2=ipstr1.split('-')
    ipstr3=ipstr2[0]
    if not check_ip(ipstr3):
        return [False,False]
    if len(ipstr2)>2:
        return [False,False]
    if len(ipstr2)==1:
        return [ipstr2[0],ipstr2[0]]
    if not check_ip(ipstr2[1]):
        if str(ipstr2[1]).isnumeric():
            ipstr4=ipstr3.split('.')
            return [ipstr2[0],"{0}.{1}.{2}.{3}".format(ipstr4[0],ipstr4[1],ipstr4[2],str(ipstr2[1]))]
    if check_ip(ipstr2[1]):
        return [ipstr2[0],ipstr2[1]]
def ip2num(ip):
    ips = [int(x) for x in ip.split('.')]
    return ips[0]<< 24 | ips[1]<< 16 | ips[2] << 8 | ips[3]
def num2ip (num):
    return '%s.%s.%s.%s' % ((num >> 24) & 0xff, (num >> 16) & 0xff, (num >> 8) & 0xff, (num & 0xff))
    #return '%s.%s.%s.%s' % ((num & 0xff000000)>>24,(num & 0x00ff0000)>>16,(num & 0x00000ff00)>>8,num & 0x000000ff)
def gen_ip(ip):
    start ,end = [ip2num(x) for x in ip.split('-')]
    return [num2ip(num) for num in range(start,end+1) if num & 0xff]
def get_ipaddr_array(ipstr):
    startip,endip=get_startNendIP(ipstr)
    if startip==False or endip==False:
        return []
    return gen_ip("%s-%s"%(startip,endip))
def get_ipaddr_arrayA(ipstr):
    ips1=ipstr.split(',')
    s2=[]
    for x in ips1:
        s1=get_ipaddr_array(x)
        for ss1 in s1:
            if ss1 not in s2:
                s2.append(ss1)
    return s2
