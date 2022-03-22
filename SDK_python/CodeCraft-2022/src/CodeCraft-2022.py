'''
Author: fujiawei0724
Date: 2022-03-18 09:27:23
LastEditors: fujiawei0724
LastEditTime: 2022-03-22 09:40:06
Description:
'''
import numpy as np
import configparser
import copy
from collections import defaultdict
import math

class Tools:

    @staticmethod
    def select_edge_nodes(available_edge_nodes, connected_number, count_info, connected_info,num):

        def check(covered_info, checked_edge_node):
            if len(connected_info[checked_edge_node]) == 0:
                return False
            for con_client in connected_info[checked_edge_node]:
                if covered_info[con_client]:
                    return False
            return True
        l = 0
        # Initialize results
        selected_edge_nodes = []
        used_available_edge_node = dict()
        for node in available_edge_nodes:
            used_available_edge_node[node] = True
        while len(selected_edge_nodes) < num :
            # print("DEBUG:select_node:{},num:{}".format(len(selected_edge_nodes),num))
        # Record the cover information of all clients
            l += 1
            covered_info = dict()
            for client in count_info.keys():
                covered_info[client] = False

            # Sort the edge nodes with the number of the connected clients
            available_edge_nodes = sorted(available_edge_nodes, key=lambda x:connected_number[x], reverse=True)

            # Traverse
            for candid_avail_edge_node in available_edge_nodes:
                # if False not in covered_info.values():
                #     break
                if not check(covered_info, candid_avail_edge_node):
                    continue
                if used_available_edge_node[candid_avail_edge_node]:
                    selected_edge_nodes.append(candid_avail_edge_node)
                    used_available_edge_node[candid_avail_edge_node] = False
                    for con_client in connected_info[candid_avail_edge_node]:
                        covered_info[con_client] = True
            
        
        # DEBUG
        # for client, covered in covered_info.items():
        #     if not covered:
                # print('DEBUG: available edge nodes could cover: {}'.format(client))
        # END DEBUG

        # print('Selected edge nodes number: {}'.format(len(selected_edge_nodes)))

        return selected_edge_nodes

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
    with open('./data/site_bandwidth.csv', 'rb') as s:
        data1 = np.loadtxt(s, str, delimiter=",")
        jiedian_number = len(data1[1:])
        # 边缘节点名称
        jiedian = []
        # 边缘节点带宽上限
        C = defaultdict()
        jiedian_ave = 0
        for i in range(jiedian_number):
            jiedian.append(data1[i + 1][0])
            C[data1[i + 1][0]] = int(data1[i + 1][1])
            jiedian_ave += int(data1[i + 1][1])
        jiedian_ave = jiedian_ave/jiedian_number
    with open('./data/demand.csv', 'rb') as f:
        data = np.loadtxt(f, str, delimiter=",")
        # 客户名称
        kehu = data[0][1:]
        kehu_number = len(kehu)
        T = len(data[1:])
        D = defaultdict(list)

        total_kehu_demnd = []
        max_kehu_demand = []
        num = []
        # 客户宽带需求
        for i in range(T):
            a = 0
            b = 0
            for j in range(kehu_number):
                D[kehu[j]].append(int(data[i + 1][j + 1]))
                a = a +int(data[i + 1][j + 1])
            total_kehu_demnd.append(a)
            b =  a/kehu_number
            max_kehu_demand.append(b)
            num.append(max((total_kehu_demnd[i] / jiedian_ave), kehu_number))
    with open('./data/qos.csv', 'rb') as q:
        data2 = np.loadtxt(q, str, delimiter=',')
        # Q[边缘节点][客户节点]=qos
        Q = defaultdict(int)
        for i in range(len(data2) - 1):
            for j in range(len(data2[0]) - 1):
                # Q[data[0][i+1]][data[j+1][0]] = int(data[i+1][j+1])
                Tools.addtwodimdict(Q, data2[i + 1][0], data2[0][j + 1], int(data2[i + 1][j + 1]))
    # print(T)3
    # print(D)
    # print(Q)
    # print(C)
    # print(qos_constraint)



    # print(num)

    # Record the connected clients number of a edge node and the available edge nodes for each client
    connected_number = defaultdict(int)
    connected_info = defaultdict(list)
    count = defaultdict(int)
    count_info = defaultdict(list)
    non_connected_num = 0
    for edge_node in jiedian:
        for client in kehu:
            if Q[edge_node][client] < qos_constraint:
                connected_number[edge_node] += 1
                connected_info[edge_node].append(client)
                count[client] += 1
                count_info[client].append(edge_node)
        if connected_number[edge_node] == 0:
            non_connected_num += 1

    # Calculate the maximum fully loaded numbers
    maximum_fully_loaded_num = int(T * 0.05)
    total_fully_num = maximum_fully_loaded_num * jiedian_number
    sum_loaded_num = 0
    # Record the current fully loaded numbers of each edge node
    fully_loaded_numbers = defaultdict(int)
    for edge_node in jiedian:
        # if connected_numer[edge_node] != 0:
        #     fully_loaded_numbers[edge_node] = 0
        fully_loaded_numbers[edge_node] = 0

    W = defaultdict(list)
    for j in range(jiedian_number):
        for t in range(T):
            W[jiedian[j]].append(0)
    # count = defaultdict(int)
    # for i in range(kehu_number):
    #     for j in range(jiedian_number):
    #         if Q[jiedian[j]][kehu[i]] < qos_constraint:
    #             count[kehu[i]] += 1

    # Record the result of the first allocation
    allocation_record = [dict() for _ in range(T)]

    # Record the fully loaded edge nodes in different timestamp
    fully_loaded_edge_nodes_record = [[] for _ in range(T)]

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
        available_num = min(num[t],len(cur_available_edge_nodes)-non_connected_num)

        # Sort the available edge nodes
        sel_edge_nodes = Tools.select_edge_nodes(cur_available_edge_nodes, connected_number, count_info, connected_info,available_num)

        # fully_loaded_edge_nodes_record[t].extend(sel_edge_nodes)
        # print(sel_edge_nodes)

        # Record the fully loaded edge nodes
        cur_fully_loaded_edge_nodes = []

        for sel_edge_node in sel_edge_nodes:

            # Calculate parameter
            # dam = max_kehu_demand[t]/C[sel_edge_node]
            dam = 1

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

            if W[sel_edge_node][t] > 0:
                # Fully loaded
                fully_loaded_numbers[sel_edge_node] += 1
                sum_loaded_num += 1
                cur_fully_loaded_edge_nodes.append(sel_edge_node)
                fully_loaded_edge_nodes_record[t].append(sel_edge_node)

            # if W[sel_edge_node][t] >= dam*C[sel_edge_node]:
            #     # Fully loaded
            #     fully_loaded_numbers[sel_edge_node] += 1
            #     cur_fully_loaded_edge_nodes.append(sel_edge_node)
            #
            #
            # else:
            #     # Not fully loaded, restore allocation information
            #     for client in kehu:
            #         restore_value = X[sel_edge_node][client]
            #         D[client][t] += restore_value
            #         W[sel_edge_node][t] -= restore_value
            #         X[sel_edge_node][client] -= restore_value
            #     break


        # Allocate remain demanding
        for i in range(kehu_number):

            # Calculate the client's connected edge nodes that have not been fully loaded at the current timestamp
            valid_ave_connected_edge_nodes_num = 0
            cur_connected_edge_node = count_info[kehu[i]]
            for con_edge_node in cur_connected_edge_node:
                if con_edge_node not in cur_fully_loaded_edge_nodes:
                    valid_ave_connected_edge_nodes_num += 1
            
            # Mandatory average allocation flag
            if valid_ave_connected_edge_nodes_num == 0:
                # print('Timestamp: {}, client: {} has no valid average allocation edge nodes.'.format(t, kehu[i]))
                valid_ave_connected_edge_nodes_num = count[kehu[i]]

            # 剩余全部分配
            orginal = D[kehu[i]][t]
            for j in range(jiedian_number):
                # if jiedian[j] == sel_edge_node:
                #     continue
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
                        if int(orginal / valid_ave_connected_edge_nodes_num) <= D[kehu[i]][t]:
                            if rest >= int(orginal / valid_ave_connected_edge_nodes_num):
                                # 分配带宽
                                X[jiedian[j]][kehu[i]] += int(orginal / valid_ave_connected_edge_nodes_num)
                                # 客户带宽分配完
                                W[jiedian[j]][t] += int(orginal / valid_ave_connected_edge_nodes_num)
                                D[kehu[i]][t] -= int(orginal / valid_ave_connected_edge_nodes_num)
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

            #     if X[jiedian[j]][kehu[i]] != 0:
            #         resu.append('<{},{}>'.format(jiedian[j], X[jiedian[j]][kehu[i]]))
            # print(','.join(resu), file=solution)
            # # print(res)
        allocation_record[t] = X
    
    # print(fully_loaded_edge_nodes_record)

    # Extend the fully loaded edge nodes in different timestamp
    for t in range(T):

        # Calculate the edge nodes has the capacity to be fully loaded
        candid_fully_loaded_edge_nodes = []
        for e_d, f_l_n in fully_loaded_numbers.items():
            if f_l_n < maximum_fully_loaded_num and connected_number[e_d] > 0:
                candid_fully_loaded_edge_nodes.append(e_d)

        # TODO: Add the logic to select the number of extended fully loaded edge nodes considering the demanding of all clients. @lw-xjtu

        # Sort candidate fully loaded edge nodes
        candid_fully_loaded_edge_nodes = sorted(candid_fully_loaded_edge_nodes, key=lambda x:fully_loaded_numbers[x])

        # Extend the fully loaded edge nodes to the average number
        for can_edge_node in candid_fully_loaded_edge_nodes:
            if len(fully_loaded_edge_nodes_record[t]) > maximum_fully_loaded_num:
                break
            if can_edge_node not in fully_loaded_edge_nodes_record[t] and len(fully_loaded_edge_nodes_record[t]) < maximum_fully_loaded_num:
                fully_loaded_edge_nodes_record[t].append(can_edge_node)
                fully_loaded_numbers[can_edge_node] += 1

    # Reallocation
    for t in range(T):

        # Get the edge nodes designed to be fully loaded at the timestamp
        designed_fully_load_nodes = fully_loaded_edge_nodes_record[t]
        for e_d in designed_fully_load_nodes:

            # Check the whole bandwidth and the used bandwidth
            cur_used_bandwidth = W[e_d][t]
            cur_all_bandwidth = C[e_d]

            # # DEBUG
            # print('For designed fully edge node: {}, all bandwidth is: {}, used bandwidth is: {}'.format(e_d, cur_all_bandwidth, cur_used_bandwidth))
            # # END DEBUG

            # Exist available bandwidth for a designed fully loaded edeg node
            if cur_used_bandwidth < cur_all_bandwidth:

                # Calculate the remained bandwidth
                remained_available_bandwidth = cur_all_bandwidth - cur_used_bandwidth

                # Get all the clients connect with the current edge node
                connected_clients = connected_info[e_d]

                for cur_con_client in connected_clients:

                    # Judge remain bandwidth
                    if remained_available_bandwidth == 0:
                        break

                    # Get the current allocatiuon situation for the current client
                    # Get the connected edge nodes with current client
                    for con_edge_node in count_info[cur_con_client]:

                        # Judge the current connected node
                        if con_edge_node in designed_fully_load_nodes:
                            continue

                        # Get the bandwidth between the client and edge node
                        cur_bandwidth = allocation_record[t][con_edge_node][cur_con_client]

                        # # DEBUG
                        # if cur_bandwidth != 0:
                        #     print('Designed fully loaded edge node: {}, connected client: {}, initial allocated edge node: {}, initial bandwidth: {}'.format(e_d, cur_con_client, con_edge_node, cur_bandwidth))
                        # # END DEBUG

                        # Reallocation
                        if cur_bandwidth > 0:

                            if cur_bandwidth <= remained_available_bandwidth:
                                allocation_record[t][con_edge_node][cur_con_client] -= cur_bandwidth
                                allocation_record[t][e_d][cur_con_client] += cur_bandwidth
                                W[e_d][t] += cur_bandwidth
                                W[con_edge_node][t] -= cur_bandwidth
                                remained_available_bandwidth -= cur_bandwidth
                            else:
                                allocation_record[t][con_edge_node][cur_con_client] -= remained_available_bandwidth
                                allocation_record[t][e_d][cur_con_client] += remained_available_bandwidth
                                W[e_d][t] += remained_available_bandwidth
                                W[con_edge_node][t] -= remained_available_bandwidth
                                remained_available_bandwidth = 0

                                # DEBUG
                                assert W[e_d][t] == C[e_d]
                                # END DEBUG

                                break
    
    # Output result
    solution = open('./output/solution.txt', 'w')
    for t in range(T):
        cur_X = allocation_record[t]
        for client in kehu:
            print('{}:'.format(client), file=solution, end='')
            resu = []
            for edge_node in jiedian:
                if cur_X[edge_node][client] != 0:
                    resu.append('<{},{}>'.format(edge_node, cur_X[edge_node][client]))
            print(','.join(resu), file=solution)
    
    fully_node = 0
    total_full = 0
    for edge_node in jiedian:
        if fully_loaded_numbers[edge_node] > 0:
            fully_node += 1
            total_full += fully_loaded_numbers[edge_node]
    # print('T:{},total_jiedian:{},fully_node:{},total_full:{}'.format(T, jiedian_number, fully_node, total_full))
    # print(fully_loaded_edge_nodes_record)
    
    # # Ouput fullly loaded edges
    # ans = 0
    # for t in range(T):
    #     ans += len(fully_loaded_edge_nodes_record[t])
    # print(ans)
    # # print(fully_loaded_numbers)
    # print(fully_loaded_edge_nodes_record)
    #
    # s = 0
    # for j in range(jiedian_number):
    #     # 总带宽排序
    #     W[jiedian[j]].sort()
    #     s += W[jiedian[j]][int(T * 0.95)]
    # print(s)
    # print(W)
    # print(D)
    # print(X)


