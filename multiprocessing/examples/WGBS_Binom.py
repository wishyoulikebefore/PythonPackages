import time
import glob
import multiprocessing
import pandas as pd
from functools import wraps
from scipy.stats import binom
import os

def timer(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        start_time = time.time()
        func(*args,**kwargs)
        end_time = time.time()
        print("共耗时%s秒" % (end_time - start_time))
    return wrapper

def get_EX(n,exp):
    for nu in range(n+1):
        if binomDict.get("%s_%s" %(n,nu)) < exp:
            return nu
        else:
            pass
    return 1         #应对n=0或者n=1

def get_pValue(mNum,n):
    return binomDict.get("%s_%s" %(n,mNum))

@timer
def reprocess(filter_file):
    print("开始处理%s" %(filter_file))
    file_name = filter_file+".tmp"
    output = open(file_name, "a")
    output.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % ("chr", "loc", "chain", "meth", "unmeth", "type", "ref", "minimum_counts(method1)", "current_pValue(method2)"))
    with open(filter_file) as f:
        for line in f:
            lineList = line.rstrip().split()
            mNum = int(lineList[3])
            umNum = int(lineList[4])
            n = min((mNum + umNum), 2000)
            exp = 0.01 * mNum / umNum if mNum * umNum > 0 else 0.01
            EX = get_EX(n, exp)
            pValue = get_pValue(mNum, n)
            output.write("%s\t%s\t%s\n" % ("\t".join(lineList[:7]), EX, pValue))
    os.remove(filter_file)
    os.rename(file_name,filter_file.replace(".CX_filtered.txt",""))

#对于不变的全局变量，可以放在main外面
#这是与process_CX_MP.py的区别所在
table = pd.read_table("/glusterfs/home/zuo_tianyu/python_script/methylation/Binom_data", header=None, names=["con", "p"])
binomDict = dict(zip(table["con"], table["p"]))

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=24)
    for filter_file in glob.glob("*filter*"):
        pool.apply_async(reprocess,args=(filter_file,))
    pool.close()
    pool.join()
