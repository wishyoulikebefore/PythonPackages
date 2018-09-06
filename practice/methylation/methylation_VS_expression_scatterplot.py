# Created by zty on 2018/9/
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
from scipy.stats import spearmanr,pearsonr
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("WGBS_RNAseq.csv",index_col=0)
methyList = df.columns[:4]
df["type"] = df.index.str[-1]

for methy_type in methyList:
    select_df = df[[methy_type,"FPKM","type"]]
    T_df = select_df[select_df["type"]=="T"]
    N_df = select_df[select_df["type"]=="N"]
    cors_T,p1 = spearmanr(T_df[methy_type],T_df["FPKM"])
    corp_T,p2 = pearsonr(T_df[methy_type],T_df["FPKM"])
    cors_N,p3 = spearmanr(N_df[methy_type],N_df["FPKM"])
    corp_N,p4 = pearsonr(N_df[methy_type],N_df["FPKM"])
    f, ax = plt.subplots(figsize=(15, 10))
    sns.scatterplot(x=methy_type,y="FPKM",hue="type",data=select_df)
    ax.set_title(methy_type)
    ax.set_xlabel("Methylation level")
    ax.legend(fontsize=12)
    annotation = "T\nSpearman:%s Pearson:%s\n\nN\nSpearman:%s Pearson:%s" %(round(cors_T,2),round(corp_T,2),round(cors_N,2),round(corp_N,2))
    ax.text(0.75,0.6,annotation,fontsize=12,bbox=dict(facecolor="white"),transform=ax.transAxes)
    f.savefig('%s_methylation_vs_expression.pdf' %(methy_type), dpi=100, bbox_inches='tight')
    print("%s绘制完成" %(methy_type))

