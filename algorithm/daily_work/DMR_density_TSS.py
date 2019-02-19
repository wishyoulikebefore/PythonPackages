# Created by zty on 2019/1/31
import matplotlib
matplotlib.use('Agg')
import sys
sys.path.append("/usr/local/python3/lib/python3.5/site-packages")
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import glob
import argparse


"""
先判断是否在gene内（要考虑多个DMR在一个基因内）
再看距离TSS的距离：20kb以内

具体思路请见ipad

添加功能：区分Tumor和Normal
"""

record = [] ## 输出两端距离TSS的值

def parse_args():
    parser = argparse.ArgumentParser(description="methylation level around TSS in different groups")
    parser.add_argument("-wd")
    parser.add_argument("-type", default="all", help="T or N or all")
    parser.add_argument("-sd")
    args = parser.parse_args()
    return args.wd,args.type,args.sd

def generate_gene_record():
    gene_record = []
    with open("/root/mnt/analysis/baidu_II/bed/knownCanonical/rename.knownCanonical.sorted.bed") as f:
        for line in f:
            lineList = line.rstrip().split()
            gene_record.append([lineList[0], int(lineList[1]), int(lineList[2]), lineList[4], lineList[5]])
    return gene_record

def process(DMR_chr,DMR_start,DMR_end):
    """
    判断DMR位置
    """
    global gene_record,pre_gene,pre_start,pre_end,pre_chain
    now_gene_info = gene_record.pop(0)
    _chr = now_gene_info[0]
    start = now_gene_info[1]
    end = now_gene_info[2]
    chain = now_gene_info[3]
    gene = now_gene_info[4]
    if _chr != DMR_chr:
        if _chr < DMR_chr:
            process(DMR_chr,DMR_start,DMR_end)
        else:
            gene_record.insert(0,now_gene_info)
            return
    elif end < DMR_start:
        pre_gene = gene
        pre_start = start
        pre_end = end
        pre_chain = chain
        process(DMR_chr,DMR_start,DMR_end)
    elif start > DMR_end:
        if pre_chain == chain == "+":
            if DMR_start - pre_start < start - DMR_end:
                record.append([DMR_start-pre_start,DMR_end-pre_start])
            else:
                record.append([start-DMR_end,start-DMR_start])
        elif pre_chain == chain == "-":
            if DMR_start - pre_end < end - DMR_end:
                record.append([DMR_start-pre_end,DMR_end-pre_end])
            else:
                record.append([end-DMR_end,end-DMR_start])
        elif pre_chain == "+" and chain == "-":
            if DMR_start - pre_start < end - DMR_end:
                record.append([DMR_start-pre_start,DMR_end-pre_start])
            else:
                record.append([end-DMR_end,end-DMR_start])
        else:
            if DMR_start - pre_end < start - DMR_end:
                record.append([DMR_start-pre_end,DMR_end-pre_end])
            else:
                record.append([start-DMR_end,start-DMR_start])
    else:
        if chain == "+":
            record.append([DMR_start-start,DMR_end-start])
        else:
            record.append([end-DMR_end,end-DMR_start])
        ### 注意多个DMR位于同一个gene内
        gene_record.insert(0,now_gene_info)

def pipeline(wd,_type,sd,gene_record):
    countList = []
    os.chdir(wd)
    for sample_pair in glob.glob("*T_*N"):
        if not os.path.isdir(sample_pair):
            continue
        gene_record = gene_record[:]
        pre_gene = ""
        pre_start = ""
        pre_end = ""
        pre_chain = ""
        print("%s开始处理" % (sample_pair))
        with open("%s/%s_denovo_metilene_CG_qval.0.05.out" %(sample_pair,sample_pair)) as f:
            for line in f:
                lineList = line.rstrip().split()
                _chr = lineList[0]
                start = int(lineList[1])
                end = int(lineList[2])
                DMR_diff = float(lineList[4])
                if _type == "T" and DMR_diff < 0:
                    continue
                elif _type == "N" and DMR_diff > 0:
                    continue
                else:
                    pass
                try:
                    process(_chr, start, end)
                except IndexError:
                    continue

    for item in record:
        start = item[0]
        end = item[1]
        for i in range(start, end + 1):
            if np.abs(i) > 20000:
                pass
            else:
                countList.append(i)

    sns.set(style="white", font_scale=2)
    f, ax = plt.subplots(figsize=(8, 8))
    sns.distplot(countList, hist=False, ax=ax)
    ax.set_xlim(-20000, 20000)
    ax.set_yticks([0,0.00005,0.0001,0.00015,0.00020])
    ax.set_xlabel("Distance to TSS(nt)",fontdict={"size": 16, "weight": "bold"})
    ax.set_ylabel("Density",fontdict={"size": 16, "weight": "bold"})
    ax.vlines(0,0,0.0002)
    f.savefig("%s/DMR_density_TSS_%s.png" %(sd,_type), dpi=100,bbox_inches='tight')

if __name__ == "__main__":
    wd,_type,sd = parse_args()
    gene_record = generate_gene_record()
    pipeline(wd,_type,sd,gene_record)
