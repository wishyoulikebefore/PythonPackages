# 2018-08-24 edit by zty
# 作用：基于Seurat生成的表达矩阵检测某些基因在各cluster的表达情况，定量，用于后续绘图
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import glob
import seaborn as sns
import os
import numpy as np

"""
各簇某个基因表达的barcodes总数：量化
---------------------------------
UMI count使用log使颜色层次化
对于0或NA值，以1替代，log2值为0
"""

def parse_args():
    parser = argparse.ArgumentParser(description="寻找特定基因在Seurat的各个簇中是否表达")
    parser.add_argument("-d",required=False,default=os.getcwd())
    parser.add_argument("-p",type=str)   #project_name
    parser.add_argument("-f")    #genes_file
    args = parser.parse_args()
    return args.d,args.p,args.f

def gen_temp_data(pro):
    cell_typeDict = {}
    for line in open("cell_type.list").readlines():
        lineList = line.rstrip().split("\t")
        cell_typeDict[lineList[0]] = lineList[1]
    barcodeDict = {}
    for file in glob.glob("cluster_barcode/*txt"):
        cluster_name = cell_typeDict.get(file.split("/")[-1].replace(".txt",""),"unrecognized")
        df = pd.read_table(file,header=None,names=["barcodes"])
        barcodesList = df["barcodes"].tolist()
        if cluster_name not in barcodeDict:          #防止多个unrecognized
            barcodeDict[cluster_name] = barcodesList
        else:
            barcodeDict[cluster_name].extend(barcodesList)
    return  barcodeDict

def expression_heatmap(expression_matrix,geneList,barcodeDict):
    """
    两种思路：1）延续之前的方法，逐个基因判断
              2）按照cluster顺序，提取dataframe求和（这个比较好，可以利用sum）
    """
    expression = expression_matrix.ix[geneList]
    UMI_countList = []
    for key,value in barcodeDict.items():
        UMI_sum =np.log2(expression[value].sum(axis=1).replace(0,1)).fillna(0)
        UMI_countList.append(UMI_sum)
    UMIs = pd.DataFrame(UMI_countList,index=barcodeDict.keys(),columns=geneList)
    UMIs.to_csv("UMI_count_sum.csv")
    f, ax = plt.subplots(figsize=(20,15))
    ax.set_title("heatmap of gene expression")
    sns.heatmap(UMIs,annot=True,cmap="BuPu",linewidths=0.5)
    f.savefig('heatmap.pdf',dpi=100, bbox_inches='tight')   #保存的图片不会出现部分内容显示不全的现象

if __name__ == "__main__":
    _dir, pro, genes = parse_args()
    geneList = [gene.strip().upper() for gene in open(genes).readlines()]
    os.chdir(os.path.join(_dir, pro))
    barcodeDict = gen_temp_data(pro)
    expression_matrix = pd.read_table("%s_expression_matrix_raw.txt" %(pro), index_col=0)
    expression_heatmap(expression_matrix,geneList,barcodeDict)
