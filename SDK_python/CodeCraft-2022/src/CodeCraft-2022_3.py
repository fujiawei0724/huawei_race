'''
Author: fujiawei0724
Date: 2022-03-18 09:27:23
LastEditors: fujiawei0724
LastEditTime: 2022-03-18 13:49:19
Description: 
'''
import numpy as np
import configparser
from collections import defaultdict

import math

class Tools:

    @staticmethod
    def select_edge_nodes(available_edge_nodes, connected_number):
        max_cover_num = 0
        res = ' '
        for edge_node in available_edge_nodes:
            if connected_number[edge_node] > max_cover_num:
                res = edge_node
                max_cover_num = connected_number[edge_node]
        assert res != ' '
        return res

    @staticmethod
    def addtwodimdict(thedict, key_a, key_b, val):
        if key_a in thedict:
            thedict[key_a].update({key_b: val})
        else:
            thedict.update({key_a:{key_b: val}})

if __name__ == '__main__':
    config = configparser.ConfigParser() # 类实例化
    # 定义参数文件路径
    path = '/data/config.ini'
    config.read(path)
    # 导入参数配置
    qos_constraint = int(config.get('config','qos_constraint'))
    # print(qos_constraint)
    # qos_constraint = 400
    #客户
    with open('/data/demand.csv','rb') as f:
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
    with open('/data/site_bandwidth.csv','rb') as s:
        data1 = np.loadtxt(s,str,delimiter=",")
        jiedian_number = len(data1[1:])
        #边缘节点名称
        jiedian = []
        #边缘节点带宽上限
        C = defaultdict()
        for i in range(jiedian_number):
            jiedian.append(data1[i+1][0])
            C[data1[i+1][0]] = int(data1[i+1][1])
    with open('/data/qos.csv','rb') as q:
        data2 = np.loadtxt(q,str,delimiter=',')
        # Q[边缘节点][客户节点]=qos
        Q = defaultdict(int)
        for i in range(len(data2)-1):
            for j in  range(len(data2[0])-1):
                # Q[data[0][i+1]][data[j+1][0]] = int(data[i+1][j+1])
                Tools.addtwodimdict(Q,data2[i+1][0],data2[0][j+1],int(data2[i+1][j+1]))
    
    # print(T)
    # print(D)
    # print(Q)
    # print(C)
    # print(qos_constraint)

    # Calculate the maximum fully loaded numbers
    maximum_fully_loaded_num = T - math.ceil(T * 0.95) - 1

    # Record the current fully loaded numbers of each edge node
    fully_loaded_numbers = defaultdict(int)
    for edge_node in jiedian:
        fully_loaded_numbers[edge_node] = 0

    # Record the connected clients number of a edge node and the available edge nodes for each client 
    connected_numer = defaultdict(int)
    connection = defaultdict(list)
    for edge_node in jiedian:
        for client in kehu:
            if Q[edge_node][client] <= qos_constraint:
                connected_numer[edge_node] += 1
                connection[client].append(edge_node)
    # print(available_edge_nodes)

    # allocation_record = dict()

    solution = open('/output/solution.txt','w')

    W = defaultdict(list)
    for j in range(jiedian_number):
        for t in range(T):
            W[jiedian[j]].append(0)
    
    for t in range(T):

        # Record the allocation detail at the current timestamp
        # X[客户节点][边缘节点]为分配带宽，先初始化为0
        X = defaultdict(int)
        for i in range(len(data2)-1):
            for j in range(len(data2[0])-1):
                Tools.addtwodimdict(X, data2[0][j + 1], data2[i + 1][0], 0)
        
        # Get the available edge nodes and its band width
        cur_available_edge_nodes = []
        for edge_node in jiedian: 
            if fully_loaded_numbers[edge_node] < maximum_fully_loaded_num:
                cur_available_edge_nodes.append(edge_node)
        if len(cur_available_edge_nodes) == 0:
            print('No available edge nodes.')
        
        # Select the max cover edge
        sel_edge_node = Tools.select_edge_nodes(cur_available_edge_nodes, connected_numer)
        fully_loaded_numbers[sel_edge_node] += 1

        # Start allocation
        sel_edge_node_avail_bandwidth = C[sel_edge_node]
        for client in kehu:
            cur_client_demand = D[client][t]
            if Q[sel_edge_node][client] >= qos_constraint:
                continue
            if sel_edge_node_avail_bandwidth < cur_client_demand:
                D[client][t] -= sel_edge_node_avail_bandwidth
                X[client][sel_edge_node] += sel_edge_node_avail_bandwidth
                W[sel_edge_node][t] += sel_edge_node_avail_bandwidth
                sel_edge_node_avail_bandwidth = 0
                break
            else:
                D[client][t] -= cur_client_demand
                sel_edge_node_avail_bandwidth -= cur_client_demand
                X[client][sel_edge_node] += cur_client_demand
                W[sel_edge_node][t] += cur_client_demand


        
        # Allocate remain demanding
        for i in range(kehu_number):
            print('{}:'.format(kehu[i]), file=solution, end='')
            res = []
            # 剩余全部分配
            for j in range(jiedian_number):
                # if jiedian[j] == sel_edge_node:
                #     continue
                # orginal = D[kehu[i]][t]
                # 客户带宽分配完毕
                # 满足约束条件
                if Q[jiedian[j]][kehu[i]] < qos_constraint:
                    # 分配总带宽不超过节点带宽上限
                    cur_bandwidth_maximum = C[jiedian[j]]
                    # if jiedian[j] == sel_edge_node:
                    #     cur_bandwidth_maximum = sel_edge_node_avail_bandwidth
                    if W[jiedian[j]][t] <= cur_bandwidth_maximum:
                        # 节点还能承受的带宽
                        rest = cur_bandwidth_maximum - W[jiedian[j]][t]
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
            print(','.join(res), file=solution)
            # print(res)
    s = 0
    for j in range(jiedian_number):
        #总带宽排序
        W[jiedian[j]].sort()
        s += W[jiedian[j]][int(T*0.95)]
    print(s)
    # print(W)
    # print(D)
    # print(X)
 

        

            

        

        
            
            
        

    
    

    
    

