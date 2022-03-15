import numpy as np
from collections import defaultdict
# 导包
import configparser
config = configparser.ConfigParser() # 类实例化
# 定义参数文件路径
path = r'D:\华为比赛\SDK\SDK_python\data\config.ini'
config.read(path)
#导入参数配置
qos_constraint = int(config.get('config','qos_constraint'))
# print(qos_constraint)
#客户
with open('D:\华为比赛\SDK\SDK_python\data\demand.csv','rb') as f:
    data = np.loadtxt(f, str, delimiter=",")
    #客户名称
    kehu = data[0][1:]
    kehu_number = len(kehu)
    T = len(data[1:])
    D = defaultdict(list)
    #客户宽带需求
    for i in range(T):
        for j in range(kehu_number):
            D[kehu[j]].append(int(data[i+1][j+1]))
with open('D:\华为比赛\SDK\SDK_python\data\site_bandwidth.csv','rb') as s:
    data1 = np.loadtxt(s,str,delimiter=",")
    jiedian_number = len(data1[1:])
    #边缘节点名称
    jiedian = []
    #边缘节点带宽上限
    C = defaultdict()
    for i in range(jiedian_number):
        jiedian.append(data1[i+1][0])
        C[data1[i+1][0]] = int(data1[i+1][1])
def addtwodimdict(thedict, key_a, key_b, val):
  if key_a in thedict:
    thedict[key_a].update({key_b: val})
  else:
    thedict.update({key_a:{key_b: val}})
with open('D:\华为比赛\SDK\SDK_python\data\qos.csv','rb') as q:
    data2 = np.loadtxt(q,str,delimiter=',')
    # Q[边缘节点][客户节点]=qos
    #X[客户节点][边缘节点]为分配带宽，先初始化为0
    Q = defaultdict(int)
    X = defaultdict(int)
    for i in range(len(data2)-1):
        for j in  range(len(data2[0])-1):
            # Q[data[0][i+1]][data[j+1][0]] = int(data[i+1][j+1])
            addtwodimdict(Q,data2[i+1][0],data2[0][j+1],int(data2[i+1][j+1]))
            addtwodimdict(X,data2[0][j+1],data2[i+1][0],0)
#初始化j节点t时刻总带宽
W = defaultdict(list)
for j in range(jiedian_number):
    for t in range(T):
        W[jiedian[j]].append(0)
for t in range(T):
    for i in range(kehu_number):
        for j in range(jiedian_number):
            #客户带宽分配完毕
            if D[kehu[i]][t] == 0:
                continue
            #满足约束条件
            if Q[jiedian[j]][kehu[i]] < qos_constraint:
                #分配总带宽不超过节点带宽上限
                if W[jiedian[j]][t] < C[jiedian[j]]:
                    #节点还能承受的带宽
                    rest = C[jiedian[j]] - W[jiedian[j]][t]
                    if rest >= D[kehu[i]][t]:
                        #分配带宽
                        X[kehu[i]][jiedian[j]] = D[kehu[i]][t]
                        #客户带宽分配完
                        D[kehu[i]][t] = 0
                    else:
                        X[kehu[i]][jiedian[j]] = rest
                        D[kehu[i]][t] -= rest
                    W[jiedian[j]][t] += X[kehu[i]][jiedian[j]]
                #分配总带宽达到节点上限
                else:
                    continue
s = 0
for j in range(jiedian_number):
    #总带宽排序
    W[jiedian[j]].sort()
    s += W[jiedian[j]][int(T*0.95)]
print(s)











