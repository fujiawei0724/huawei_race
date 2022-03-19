###
 # @Author: fujiawei0724
 # @Date: 2022-03-19 22:44:40
 # @LastEditors: fujiawei0724
 # @LastEditTime: 2022-03-19 23:07:06
 # @Description: Process the results from different data to generate the final result
### 

comp=60
for i in {60..99}
do
    let index=$i-$comp
    python ./CodeCraft-2022/src/tester.py $index
done









