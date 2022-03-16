
import numpy as np
from collections import defaultdict
# 导包
import configparser


config = configparser.ConfigParser() # 类实例化
# 定义参数文件路径
path = './data/config.ini'
config.read(path)
# 导入参数配置
qos_constraint = int(config.get('config','qos_constraint'))
# print(qos_constraint)
# qos_constraint = 400
#客户
with open('./data/demand.csv','rb') as f:
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
with open('./data/site_bandwidth.csv','rb') as s:
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
with open('./data/qos.csv','rb') as q:
    data2 = np.loadtxt(q,str,delimiter=',')
    # Q[边缘节点][客户节点]=qos
    Q = defaultdict(int)
    for i in range(len(data2)-1):
        for j in  range(len(data2[0])-1):
            # Q[data[0][i+1]][data[j+1][0]] = int(data[i+1][j+1])
            addtwodimdict(Q,data2[i+1][0],data2[0][j+1],int(data2[i+1][j+1]))
count = defaultdict(int)
#统计t时刻对应i节点符合要求的边缘节点数，然后进行平均分配
for i in range(kehu_number):
    for j in range(jiedian_number):
        if Q[jiedian[j]][kehu[i]] < qos_constraint:
            count[kehu[i]] += 1
# print(count)
solution = open('./output/solution.txt','w')
#初始化j节点t时刻总带宽
# print(jiedian_number)
W = defaultdict(list)
for j in range(jiedian_number):
    for t in range(T):
        W[jiedian[j]].append(0)
for t in range(T):
    # X[客户节点][边缘节点]为分配带宽，先初始化为0
    X = defaultdict(int)
    for i in range(len(data2)-1):
        for j in  range(len(data2[0])-1):
            addtwodimdict(X, data2[0][j + 1], data2[i + 1][0], 0)
    for i in range(kehu_number):
        print('{}:'.format(kehu[i]), file=solution,end='')
        res = []
        orginal = D[kehu[i]][t]
        #均匀分配
        for j in range(jiedian_number):
            #客户带宽分配完毕
            #满足约束条件
            if D[kehu[i]][t] == 0:
                continue
            if Q[jiedian[j]][kehu[i]] < qos_constraint:
                #分配总带宽不超过节点带宽上限
                if W[jiedian[j]][t] < C[jiedian[j]]:
                    #节点还能承受的带宽
                    rest = C[jiedian[j]] - W[jiedian[j]][t]
                    if rest >= int(orginal/count[kehu[i]]):
                        #分配带宽
                        X[kehu[i]][jiedian[j]] = int(orginal/count[kehu[i]])
                        #客户带宽分配完
                        D[kehu[i]][t] -= X[kehu[i]][jiedian[j]]
                    else:
                        X[kehu[i]][jiedian[j]] = rest
                        D[kehu[i]][t] -= X[kehu[i]][jiedian[j]]
                    W[jiedian[j]][t] += X[kehu[i]][jiedian[j]]
                #分配总带宽达到节点上限
                else:
                    continue
        # #反向均匀分配
        # for j in range(jiedian_number-1,-1,-1):
        #     # orginal = D[kehu[i]][t]
        #     # 客户带宽分配完毕
        #     # 满足约束条件
        #     if Q[jiedian[j]][kehu[i]] < qos_constraint:
        #         # 分配总带宽不超过节点带宽上限
        #         if W[jiedian[j]][t] < C[jiedian[j]]:
        #             # 节点还能承受的带宽
        #             rest = C[jiedian[j]] - W[jiedian[j]][t]
        #             if rest >= int(D[kehu[i]][t]/kehu_number):
        #                 # 分配带宽
        #                 X[kehu[i]][jiedian[j]] += int(D[kehu[i]][t]/kehu_number)
        #                 # 客户带宽分配完
        #                 W[jiedian[j]][t] += int(D[kehu[i]][t]/kehu_number)
        #                 D[kehu[i]][t] -= int(D[kehu[i]][t]/kehu_number)
        #             else:
        #                 X[kehu[i]][jiedian[j]] += rest
        #                 W[jiedian[j]][t] += rest
        #                 D[kehu[i]][t] -= rest
        #
        #         # 分配总带宽达到节点上限
        #         else:
        #             continue
        # 剩余全部分配
        for j in range(jiedian_number - 1, -1, -1):
            # orginal = D[kehu[i]][t]
            # 客户带宽分配完毕
            # 满足约束条件
            if Q[jiedian[j]][kehu[i]] < qos_constraint:
                # 分配总带宽不超过节点带宽上限
                if W[jiedian[j]][t] < C[jiedian[j]]:
                    # 节点还能承受的带宽
                    rest = C[jiedian[j]] - W[jiedian[j]][t]
                    if rest >= D[kehu[i]][t]:
                        # 分配带宽
                        X[kehu[i]][jiedian[j]] += D[kehu[i]][t]
                        # 客户带宽分配完
                        W[jiedian[j]][t] += D[kehu[i]][t]
                        D[kehu[i]][t] = 0
                    else:
                        X[kehu[i]][jiedian[j]] += rest
                        W[jiedian[j]][t] += rest
                        D[kehu[i]][t] -= rest

                # 分配总带宽达到节点上限
                else:
                    continue
            if X[kehu[i]][jiedian[j]] != 0:
                res.append('<{},{}>'.format(jiedian[j], X[kehu[i]][jiedian[j]]))
        # if D[kehu[i]][t] != 0:
        #     print(D[kehu[i]][t])
        print(','.join(res), file=solution)
s = 0
for j in range(jiedian_number):
    #总带宽排序
    W[jiedian[j]].sort()
    s += W[jiedian[j]][int(T*0.95)]
# print(s)











