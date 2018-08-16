import pandas as pd
import time
import glob
import multiprocessing
from functools import wraps,partial

"""
处理数据背景：甲基化样本共200+，每个文件10亿+行，需要从中挑出在甲基化芯片中50万+条序列中的位点（每条序列50bp长）
速度优化：1）甲基化样本文件不是按照染色体顺序排列，但每条染色体内部的位置都是排过序的
          -->需要先对芯片位点排序，按照chr提取起点位置列表至字典中方便调用
          2）judge()函数中的搜索优化：终止+位点列表的删减（已检出位点之前所有位点的删除，避免无效搜索）
          3）输出每个样本每条染色体的运行时间和总运行时间
          4）多进程处理，加快速度（注意decorator的坑）

优化问题：每个样本都需要传入chr_locDict，可以使用functools.partial冻起来
"""

def process_chip():
    chip = "/glusterfs/home/zuo_tianyu/python_script/methylation/human_methylation_450k_beadchip_array.txt"
    table = pd.read_table(chip,dtype={"CHR":str})
    select_columns = ["CHR","MAPINFO"]
    df = table[select_columns].dropna()
    df.rename(columns={"MAPINFO":"start","CHR":"chr"},inplace=True)    #芯片都是50bp
    df["chr"] = "chr"+df["chr"]
    df.sort_values(by=["chr","start"],inplace=True)
    df.set_index("chr",inplace=True)
    chrList = df.index.unique()
    chr_locDict = {}
    for chr_name in chrList:
        chr_locDict[chr_name] = df.ix[chr_name]["start"].tolist()
    print("芯片所用序列位点已获得")
    return chr_locDict

def timer(func):
    """
    multiprocessing不支持装饰器直接使用（因为装饰器修饰后的函数会丢失原有函数名，导致不可pickle）
    使用functools.wraps解决（注解底层包装函数）
    """
    @wraps(func)
    def wrapper(*args,**kwargs):
        start_time = time.time()
        func(*args,**kwargs)
        end_time = time.time()
        print("%s" % (end_time - start_time))
    return wrapper

@timer
def process_sample(chr_locDict,CX_file):
    copyDict = chr_locDict
    print("%s开始处理" % (CX_file))
    sample_name = CX_file.replace(".*", "")
    output = open(sample_name + ".CX_filtered.txt", "a")
    last_chr = ""
    chr_process_time = time.time()
    with open(CX_file) as f:
        for line in f:
            lineList = line.rstrip().split()
            _chr = lineList[0]
            loc = lineList[1]
            if "_" in _chr or _chr == "chrM":
                continue
            if monitor(last_chr,_chr):
                print("%s的%s处理共耗时%s" %(sample_name,last_chr,time.time()-chr_process_time))
                chr_process_time = time.time()
                last_chr = _chr
            else:
                pass
            this_judge = judge(_chr, loc,copyDict)
            if this_judge:
                output.write(line)
                copyDict = this_judge
            else:
                pass
    print("%s处理完成" % (CX_file))
    f.close()
    output.close()

#输出各chr的处理时间
def monitor(last_chr,now_chr):
    if last_chr != now_chr:
        return 1
    else:
        return

def judge(_chr,loc,chr_locDict):
    chip_loc = chr_locDict[_chr]
    loc = int(loc)
    for nu,loci in enumerate(chip_loc):
        loci = int(loci)
        if loc < loci:
            return
        elif loc >= loci and loc <= loci+49:
            del chip_loc[:nu]
            chr_locDict[_chr] = chip_loc
            return chr_locDict
        else:
            pass

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=24)
    chr_locDict = process_chip()
    process_sample_partial = partial(process_sample,chr_locDict)
    for CX_file in glob.glob("*txt"):
        pool.apply_async(process_sample_partial,args=(CX_file,))
    pool.close()
    pool.join()

