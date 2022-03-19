###
 # @Author: fujiawei0724
 # @Date: 2022-03-19 21:15:30
 # @LastEditors: fujiawei0724
 # @LastEditTime: 2022-03-19 22:42:24
 # @Description: Generate random data
### 

comp=60
for i in {60..99}
do
    let index=$i-$comp
    index_str="$index"
    python data_gen.py data_$index $i
    echo "Output data group $index"
done




