# Created by zty on 2018/12/20
import pandas as pd
import numpy as np
import argparse
from scipy.stats import binom
import os
import glob
import multiprocessing
import time
from functools import wraps

def parse_args():
    parser = argparse.ArgumentParser(description="methylated_gene_body")
    parser.add_argument("-d")
    parser.add_argument("-p",required=False,default=0.05)       #significant
    args = parser.parse_args()
    return args.d,args.p

def timer(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        start_time = time.time()
        func(*args,**kwargs)
        end_time = time.time()
        print("共耗时%s秒" % (end_time - start_time))
    return wrapper

def binom_test(m,n,p):
    cum_prob = binom.pmf(range(m),n,p).sum()
    if cum_prob >= 1:
        pValue = binom.pmf(range(m,n+1),n,p).sum()
    else:
        pValue = 1-cum_prob
    return pValue

def process(df,pValue):
    df = df[["Total_CG","Total_covered_CG","CG_Methy_density","CG_Methy_level","CG_Methy_level_average"]]
    df["CG_Methy_loc"] = df.apply(lambda x:np.ceil(x["Total_covered_CG"]*x["CG_Methy_density"]/100),axis=1)
    CG_methy_sum = df["CG_Methy_loc"].sum()
    Total_covered_CG_whole = df["Total_covered_CG"].sum()
    Pcg = CG_methy_sum / Total_covered_CG_whole
    df["binom_test"] = df.apply(lambda x:binom_test(x["CG_Methy_loc"].astype(int),x["Total_covered_CG"].astype(int),Pcg),axis=1)
    methylated_df = df[df["binom_test"] < pValue]
    return methylated_df

@timer
def start_analysis(wd,sample_id):
    print("开始处理%s" % (sample_id))
    df = pd.read_table("%s/%s/%s.promoter.np1kb.filter.stat.all.xls" % (wd,sample_id,sample_id), index_col=0)
    methylated_df = process(df, pValue)
    methylated_df.to_csv("%s/%s/%s.methylated.promoter.np1kb.txt" % (wd,sample_id,sample_id), sep="\t")
    df2 = pd.read_table("%s/%s/%s.promoter.p2kb.filter.stat.all.xls" % (wd,sample_id,sample_id), index_col=0)
    methylated_df = process(df2, pValue)
    methylated_df.to_csv("%s/%s/%s.methylated.promoter.p2kb.txt" % (wd,sample_id,sample_id), sep="\t")
    df3 = pd.read_table("%s/%s/%s.gene.filter.stat.all.xls" % (wd,sample_id,sample_id), index_col=0)
    methylated_df = process(df3, pValue)
    methylated_df.to_csv("%s/%s/%s.methylated.gene.body.txt" % (wd,sample_id,sample_id), sep="\t")
    print("%s处理完毕" % (sample_id))

if __name__ == "__main__":
    wd,pValue = parse_args()
    os.chdir(wd)
    pool = multiprocessing.Pool(processes=12)
    for sample_id in glob.glob("*[N|T]"):
        pool.apply_async(start_analysis,args=(wd,sample_id,))
    pool.close()
    pool.join()
