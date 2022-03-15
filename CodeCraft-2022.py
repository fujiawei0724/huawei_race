import numpy as np
from collections import defaultdict
# 导包
#付佳伟是憨批
import configparser
config = configparser.ConfigParser() # 类实例化
# 定义参数文件路径
path = r'D:\华为比赛\SDK\SDK_python\data\config.ini'
config.read(path)
#导入参数配置
qos_constraint = config.get('config','qos_constraint')
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
    Q = defaultdict()
    for i in range(len(data2)-1):
        for j in  range(len(data2[0])-1):
            # Q[data[0][i+1]][data[j+1][0]] = int(data[i+1][j+1])
            addtwodimdict(Q,data2[i+1][0],data2[0][j+1],int(data2[i+1][j+1]))
