# Created by zty on 2018/10/26
import matplotlib.pyplot as plt
import argparse
from dateparser import parse
import pandas as pd
import seaborn as sns

"""
提取N和T样本的WGBS数据大小和运行时间
grep start *o | sed 's/2018.*/2018/' | sed 's/\./ /g' | awk '{print $2 "\t" $5 "\t" $6 "\t" $7 "\t" $9}'
grep finish *o | sed 's/2018.*/2018/' | sed 's/\./ /g' | awk '{print $2 "\t" $5 "\t" $6 "\t" $7 "\t" $9}'

du -sh * | sed '1d' | sed 's/Sample_//' | sed 's/G//' | awk '{print $2 "\t" $1}'

格式：
R18039956LF01-BDESCCMET194-N    Oct     9       13:20:52        2018
R18039957LF01-BDESCCMET194-T    Oct     9       13:21:45        2018

结论：耗时 = 2.5h * volume(G)  大约
"""

def parse_args():
    parser = argparse.ArgumentParser(description="WGBS样本数据大小与运算时间统计")
    parser.add_argument("-s", help="开始时间log")
    parser.add_argument("-e", help="结束时间log")
    parser.add_argument("-v", help="样本数据大小")
    args = parser.parse_args()
    return args.s,args.e,args.v

def process(start_log,end_log,vol):
    start_df = pd.read_table(start_log,sep="\t",header=None,names=["sample","month","day","time","year"],index_col=0)
    end_df = pd.read_table(end_log,sep="\t",header=None,names=["sample","month","day","time","year"],index_col=0)
    start_df["start_time"] = start_df.apply(lambda x:parse("%s %s %s %s" %(x["year"],x["month"],x["day"],x["time"])),axis=1)
    start_df["start_time"] = start_df.apply(lambda x:pd.Period(x["start_time"],freq="H"),axis=1)
    end_df["end_time"] = end_df.apply(lambda x:parse("%s %s %s %s" %(x["year"],x["month"],x["day"],x["time"])),axis=1)
    end_df["end_time"] = end_df.apply(lambda x:pd.Period(x["end_time"], freq="H"), axis=1)
    start_df.drop(columns=["month","day","time","year"],inplace=True)
    end_df.drop(columns=["month","day","time","year"],inplace=True)
    merge_df = start_df.join(end_df,how="inner")
    merge_df["time_cost"] = merge_df["end_time"]-merge_df["start_time"]
    vol_df = pd.read_table(vol,sep="\t",header=None,names=["sample","volume"],index_col=0)
    merge_df = merge_df.join(vol_df,how="inner")
    return merge_df

def plot(merge_df):
    sns.lmplot(x="volume",y="time_cost",data=merge_df)
    plt.show()

if __name__ == "__main__":
    start_log,end_log,vol = parse_args()
    merge_df = process(start_log,end_log,vol)
    plot(merge_df)
