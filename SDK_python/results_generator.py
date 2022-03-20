'''
Author: fujiawei0724
Date: 2022-03-20 09:17:25
LastEditors: fujiawei0724
LastEditTime: 2022-03-20 09:22:39
Description: 
'''

import csv

if __name__ == '__main__':
    res_sum = 0
    with open('./random_solutions/final_result.csv', 'r') as f:
        csv_reader = csv.reader(f)
        for line in csv_reader:
            res_sum += float(line[1])
    print('Final result: {}'.format(res_sum))
