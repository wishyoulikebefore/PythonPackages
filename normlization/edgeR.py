import pandas as pd
import numpy as np
import argparse

"""
假定输入两个样本
"""

def parse_args():
    parser = argparse.ArgumentParser(description="模拟edgeR对RNAseq的处理")
    parser.add_argument("count_file")               #count.data
    parser.add_argument("ctrl_index")
    parser.add_argument("case_index")
    parser.add_argument("ctrl_name")
    parser.add_argument("case_name")
    parser.add_argument("-p",required=False,default=0.05 )
    parser.add_argument("-fc",required=False,default=2)
    args = parser.parse_args()
    return args.count_file, args.ctrl_index, args.case_index, args.ctrl_name, args.case_name, args.p, args.fc

def preprocess(df):
    df = df.ix[df.any(axis=1)]
    samples = df.columns
    f75 = df.apply(lambda x:np.percentile(x,75))
    ref_column = np.argmin(abs(f75-np.mean(f75)))
    normalized_factorDict = {}
    for item in samples:
        if item == ref_column:
            normalized_factorDict[item] = 1
        else:
            normalized_factorDict[item] = cal_normalize_factor(df,item,ref_column)
    return normalized_factorDict

def cal_normalize_factor(df,obs,ref,logratioTrim=0.3,sumTrim=0.05,cutoff=-1e10,weight=True):
    nO = df[obs].sum()       #样本总reads数
    nR = df[ref].sum()
    df["M"] = np.log2(df[obs]/nO/(df[ref]/nR))                               #gene-wise log-fold change    log2FC （Fold Change）
    df["A"] = (np.log2(df[obs]/nO) + np.log2(df[ref]/nR))/2                  #absolute expression levels   mean_logCPM
    # M和A用作绘制MA plot
    df["var"] = (nO-df[obs])/nO/df[obs] + (nR-df[ref])/nR/df[ref]               #approximate asymptotic variances
    filter_df = df.ix[(df["M"] != np.inf) & (df["M"] != -np.inf) & (df["M"] != np.nan) &
                      (df["A"] != -np.inf) & (df["A"] > cutoff)]          #排除0的影响
    if filter_df["M"].abs().max() < 1e-6:
        return
    #TMM normalization （trimmed mean of M-values）
    #删除M值上下30%，A值上下5%
    filter_genes_num = len(filter_df)
    low_L = np.floor(filter_genes_num*logratioTrim)
    high_L = filter_genes_num - low_L
    low_A = np.floor(filter_genes_num*sumTrim)
    high_A = filter_genes_num - low_A
    sort_M = df["M"].sort_values(ascending=True).tolist()
    sort_A = df["A"].sort_values(ascending=True).tolist()
    low_L_value, high_L_value = sort_M[int(low_L)], sort_M[int(high_L)]
    low_A_value, high_A_value = sort_A[int(low_A)], sort_A[int(high_A)]
    keep_df = filter_df.ix[(low_L_value <= filter_df["M"]) &(filter_df["M"] <= high_L_value) &
                           (low_A_value <= filter_df["A"]) & (filter_df["A"] <= high_A_value)]
    if weight:
        normalize_factor = np.sum(keep_df["M"]/keep_df["var"])/np.sum(1/keep_df["var"])
    else:
        normalize_factor = keep_df["M"].mean()
    return 2**normalize_factor

def cal_cpm(df,ctrl_index,case_index,normalized_factorDict):
    #get counts per million
    analysis_samples = ctrl_index + case_index
    filter_df = df[analysis_samples]
    sum_reads = filter_df.sum()
    normalized_factor = [normalized_factorDict.get(item) for item in analysis_samples]
    corrected_cpm = filter_df*normalized_factor*1000000/sum_reads
    corrected_cpm.to_csv("corrected_cpm.csv",sep="\t")
    keep = corrected_cpm[(corrected_cpm>1).any(axis=1)]      #排除cpm都小于1的基因
    return keep

def parse_group(ctrl_index,case_index,ctrl_name,case_name):
    group_info = [ctrl_name]*len(ctrl_index)+[case_name]*len(case_index)
    group_df = pd.DataFrame(group_info,index=ctrl_index+case_index,columns=["group"])
    return group_df

if __name__ == "__main__":
    count_file, ctrl_index, case_index, ctrl_name, case_name, p, fc = parse_args()
    ctrl_index = ctrl_index.split(",")
    case_index = case_index.split(",")
    df = pd.read_table(count_file,index_col=0)
    normalized_factorDict = preprocess(df)
    dge = cal_cpm(df,ctrl_index,case_index,normalized_factorDict)
    group_df = parse_group(ctrl_index,case_index,ctrl_name,case_name)
