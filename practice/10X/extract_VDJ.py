# Created by zty on 2018/10/11
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os

"""
提取重链和轻链组合
会出现某种clonetype只有一条链或多于2条链的情况（）

利用文件
consensus_annotations.csv
clonotypes.csv
"""

def parse_args():
    parser = argparse.ArgumentParser(description="统计10X VDJ数据")
    parser.add_argument("-d",nargs="+",help="sample_dir")
    parser.add_argument("-n",required=False,default=10000,help="选择前多少个clonetype")
    args = parser.parse_args()
    return args.d,args.n

def process(sample_dir,top):
    """
    从clonetype.csv中提取各clonetype的频数、频率、CDR3各条链的aa
    注意cdr3s_aa这列重链和轻链使用；分割
    """
    clonetype_file = "%s/outs/clonotypes.csv" %(sample_dir)
    annotation_file = "%s/outs/consensus_annotations.csv" %(sample_dir)
    top_clonetype_df = pd.read_csv(clonetype_file, index_col=0).ix[:top,:]
    annotation_df = pd.read_csv(annotation_file,index_col=0)
    merge_df = top_clonetype_df.join(annotation_df, how="inner").sort_values(by="frequency", ascending=False)
    merge_df = merge_df[["frequency", "proportion", "length", "chain", "v_gene", "d_gene", "j_gene", "cdr3"]]
    filtered_df = merge_df.rename(columns={"v_gene": "V_gene", "d_gene": "D_gene", "j_gene": "J_gene", "cdr3": "CDR3"})
    sample_name = sample_dir.split("/")[-1]
    filtered_df.to_csv("%s_merge.csv" %(sample_name))
    return filtered_df

def compare(df1,df2):
    df1["V_J"] = df1.apply(lambda x: x["V_gene"] + "_" + x["J_gene"], axis=1)
    df1 = df1[["proportion", "chain", "V_J"]]
    pivot_df1 = df1.pivot_table(values="proportion", index="V_J", columns="chain", aggfunc="sum")
    df2["V_J"] = df2.apply(lambda x: x["V_gene"] + "_" + x["J_gene"], axis=1)
    df2 = df2[["proportion", "chain", "V_J"]]
    pivot_df2 = df1.pivot_table(values="proportion", index="V_J", columns="chain", aggfunc="sum")
    merge_df = df1.join(df2, how="outer", lsuffix='_1', rsuffix='_2')
    """
    绘制TRA和TRB V-J 前十上调和下调的柱状图，
    """

if __name__ == "__main__":
    samples_dir,top = parse_args()
    for sample_dir in samples_dir:
        process(sample_dir,top)
