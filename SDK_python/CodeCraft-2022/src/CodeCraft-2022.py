'''
Author: fujiawei0724
Date: 2022-03-18 09:27:23
LastEditors: fujiawei0724
LastEditTime: 2022-03-20 12:07:54
Description:
'''
import numpy as np
import configparser
import copy
from collections import defaultdict
import math

class Tools:

    @staticmethod
    def select_edge_nodes(available_edge_nodes, connected_number):

        # Provide the connected information
        available_edge_nodes_info = dict()
        for edge_node in available_edge_nodes:
            available_edge_nodes_info[edge_node] = connected_number[edge_node]

        # Sort
        available_edge_nodes_info = sorted(available_edge_nodes_info.items(), key=lambda x: x[1], reverse=True)

        return list(dict(available_edge_nodes_info).keys())

    @staticmethod
    def addtwodimdict(thedict, key_a, key_b, val):
        if key_a in thedict:
            thedict[key_a].update({key_b: val})
        else:
            thedict.update({key_a: {key_b: val}})


if __name__ == '__main__':
    config = configparser.ConfigParser()  # 类实例化
    # 定义参数文件路径
    path = './data/config.ini'
    config.read(path)
    # 导入参数配置
    qos_constraint = int(config.get('config', 'qos_constraint'))
    # print(qos_constraint)
    # qos_constraint = 400
    # 客户
    with open('./data/demand.csv', 'rb') as f:
        data = np.loadtxt(f, str, delimiter=",")
        # 客户名称
        kehu = data[0][1:]
        kehu_number = len(kehu)
        T = len(data[1:])
        D = defaultdict(list)
        a = 0
        max_kehu_demand = []
        # 客户宽带需求
        for i in range(T):
            for j in range(kehu_number):
                D[kehu[j]].append(int(data[i + 1][j + 1]))
                a = a +int(data[i + 1][j + 1])
            a =  a/kehu_number
            max_kehu_demand.append(a)

    with open('./data/site_bandwidth.csv', 'rb') as s:
        data1 = np.loadtxt(s, str, delimiter=",")
        jiedian_number = len(data1[1:])
        # 边缘节点名称
        jiedian = []
        # 边缘节点带宽上限
        C = defaultdict()
        for i in range(jiedian_number):
            jiedian.append(data1[i + 1][0])
            C[data1[i + 1][0]] = int(data1[i + 1][1])
    with open('./data/qos.csv', 'rb') as q:
        data2 = np.loadtxt(q, str, delimiter=',')
        # Q[边缘节点][客户节点]=qos
        Q = defaultdict(int)
        for i in range(len(data2) - 1):
            for j in range(len(data2[0]) - 1):
                # Q[data[0][i+1]][data[j+1][0]] = int(data[i+1][j+1])
                Tools.addtwodimdict(Q, data2[i + 1][0], data2[0][j + 1], int(data2[i + 1][j + 1]))

    # print(T)
    # print(D)
    # print(Q)
    # print(C)
    # print(qos_constraint)

    # Calculate the maximum fully loaded numbers
    maximum_fully_loaded_num = int(T * 0.04)

    # Record the current fully loaded numbers of each edge node
    fully_loaded_numbers = defaultdict(int)
    for edge_node in jiedian:
        fully_loaded_numbers[edge_node] = 0

    # Record the connected clients number of a edge node and the available edge nodes for each client
    connected_numer = defaultdict(int)
    count = defaultdict(int)
    for edge_node in jiedian:
        for client in kehu:
            if Q[edge_node][client] < qos_constraint:
                connected_numer[edge_node] += 1
                count[client] += 1
    # print(available_edge_nodes)

    # allocation_record = dict()

    solution = open('./output/solution.txt', 'w')

    W = defaultdict(list)
    for j in range(jiedian_number):
        for t in range(T):
            W[jiedian[j]].append(0)
    # count = defaultdict(int)
    # for i in range(kehu_number):
    #     for j in range(jiedian_number):
    #         if Q[jiedian[j]][kehu[i]] < qos_constraint:
    #             count[kehu[i]] += 1

    for t in range(T):

        # Record the allocation detail at the current timestamp
        # X[边缘节点]为分配带宽，先初始化为0

        X = defaultdict(int)
        for i in range(jiedian_number):
            for j in range(kehu_number):
                Tools.addtwodimdict(X, jiedian[i], kehu[j], 0)

        # Get the available edge nodes and its band width
        cur_available_edge_nodes = []
        for edge_node in jiedian:
            if fully_loaded_numbers[edge_node] < maximum_fully_loaded_num:
                cur_available_edge_nodes.append(edge_node)
        # if len(cur_available_edge_nodes) == 0:
        #     print('No available edge nodes.')

        # Sort the available edge nodes
        sel_edge_nodes = Tools.select_edge_nodes(cur_available_edge_nodes, connected_numer)
        # print(sel_edge_nodes)

        for sel_edge_node in sel_edge_nodes:

            # Calculate parameter
            dam = max_kehu_demand[t]/C[sel_edge_node]
            # dam = 1

            # Start allocation
            sel_edge_node_avail_bandwidth = C[sel_edge_node]
            # print(sel_edge_node_avail_bandwidth)
            kehu = sorted(kehu, key=lambda x:D[x][t], reverse=True)
            for client in kehu:
                cur_client_demand = D[client][t]
                if Q[sel_edge_node][client] < qos_constraint:
                    if sel_edge_node_avail_bandwidth < cur_client_demand:
                        D[client][t] -= sel_edge_node_avail_bandwidth
                        X[sel_edge_node][client] += sel_edge_node_avail_bandwidth
                        W[sel_edge_node][t] += sel_edge_node_avail_bandwidth
                        sel_edge_node_avail_bandwidth = 0
                        break
                    else:
                        D[client][t] -= cur_client_demand
                        sel_edge_node_avail_bandwidth -= cur_client_demand
                        X[sel_edge_node][client] += cur_client_demand
                        W[sel_edge_node][t] += cur_client_demand

            if W[sel_edge_node][t] > dam*C[sel_edge_node]:
                # Fully loaded
                fully_loaded_numbers[sel_edge_node] += 1
            else:
                # Not fully loaded, restore allocation information
                for client in kehu:
                    restore_value = X[sel_edge_node][client]
                    D[client][t] += restore_value
                    W[sel_edge_node][t] -= restore_value
                    X[sel_edge_node][client] -= restore_value
                break

        # Allocate remain demanding
        for i in range(kehu_number):
            print('{}:'.format(kehu[i]), file=solution, end='')
            resu = []
            # 剩余全部分配
            for j in range(jiedian_number):
                # if jiedian[j] == sel_edge_node:
                #     continue
                orginal = D[kehu[i]][t]
                # 客户带宽分配完毕
                # 满足约束条件
                # if D[client][t] == 0:
                #     continue
                if Q[jiedian[j]][kehu[i]] < qos_constraint:
                    # 分配总带宽不超过节点带宽上限
                    cur_bandwidth_maximum = C[jiedian[j]]
                    # if jiedian[j] == sel_edge_node:
                    #     cur_bandwidth_maximum = sel_edge_node_avail_bandwidth
                    if W[jiedian[j]][t] <= cur_bandwidth_maximum:
                        # 节点还能承受的带宽
                        rest = cur_bandwidth_maximum - W[jiedian[j]][t]
                        if int(orginal / count[kehu[i]]) <= D[kehu[i]][t]:
                            if rest >= int(orginal / count[kehu[i]]):
                                # 分配带宽
                                X[jiedian[j]][kehu[i]] += int(orginal / count[kehu[i]])
                                # 客户带宽分配完
                                W[jiedian[j]][t] += int(orginal / count[kehu[i]])
                                D[kehu[i]][t] -= int(orginal / count[kehu[i]])
                            else:
                                X[jiedian[j]][kehu[i]] += rest
                                W[jiedian[j]][t] += rest
                                D[kehu[i]][t] -= rest

                    # 分配总带宽达到节点上限
                    else:
                        continue
            # print(D[-1])
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
                            X[jiedian[j]][kehu[i]] += D[kehu[i]][t]
                            # 客户带宽分配完
                            W[jiedian[j]][t] += D[kehu[i]][t]
                            D[kehu[i]][t] = 0
                        else:
                            X[jiedian[j]][kehu[i]] += rest
                            W[jiedian[j]][t] += rest
                            D[kehu[i]][t] -= rest
                    else:
                        continue

                if X[jiedian[j]][kehu[i]] != 0:
                    resu.append('<{},{}>'.format(jiedian[j], X[jiedian[j]][kehu[i]]))
            print(','.join(resu), file=solution)
            # print(res)
    s = 0
    for j in range(jiedian_number):
        # 总带宽排序
        W[jiedian[j]].sort()
        s += W[jiedian[j]][int(T * 0.95)]
    print(s)
    # print(W)
    # print(D)
    # print(X)


