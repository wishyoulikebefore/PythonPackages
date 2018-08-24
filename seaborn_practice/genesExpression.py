# 2018-08-09 edit by zty
# 作用：基于Seurat生成的表达矩阵检测某些基因在各cluster的表达情况，定量，用于后续绘图
import matplotlib
matplotlib.use('Agg')     #针对linux
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import glob
import seaborn as sns
import os
import numpy as np

"""
UMI count使用log使颜色层次化
对于0或NA值，以1替代，log2值为0
"""

def get_barcodeDict():
    cell_typeDict = {}
    for line in open("cell_type.list").readlines():       #指定的cell_type
        lineList = line.rstrip().split("\t")
        cell_typeDict[int(lineList[0])] = lineList[1]
    barcodeDict = {}
    for file in glob.glob("cluster_barcode/*txt"):
        cluster_index = int(file.split("/")[-1].replace(".txt", ""))
        df = pd.read_table(file,header=None,names=["barcodes"])
        barcodesList = df["barcodes"].tolist()
        cell_name = cell_typeDict.get(cluster_index, "unrecognized")
        barcodeDict[cell_name] = barcodesList
    return barcodeDict

def expression_heatmap(geneList,barcodeDict):
    expression = table.ix[geneList]
    UMI_countList = []
    for key,value in barcodeDict.items():
        UMI_sum =np.log2(expression[value].sum(axis=1).replace(0,1)).fillna(0)
        UMI_countList.append(UMI_sum)
    UMIs = pd.DataFrame(UMI_countList,index=barcodeDict.keys(),columns=geneList)
    f, ax = plt.subplots(figsize=(20,12))
    ax.set_title("8个基因在10个簇中表达量的热力图")
    ax.set_xlabel("genes",fontsize=10)
    ax.set_ylabel("表达量(log2)",fontsize=10)
    sns.heatmap(UMIs,annot=True,cmap="BuPu",linewidths=0.5)
    f.savefig('heatmap.png',dpi=100, bbox_inches='tight')   #保存的图片不会出现部分内容显示不全的现象

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="寻找特定基因在Seurat的各个簇中是否表达")
    parser.add_argument("-p", required=False, default=os.getcwd())
    parser.add_argument("gene_file")
    parser.add_argument("project", type=str)
    parser.add_argument("-o", required=False)
    args = parser.parse_args()
    geneList = [gene.strip().upper() for gene in open(args.gene_file).readlines()]
    os.chdir(os.path.join(args.p, args.project))
    table = pd.read_table(args.project + "_expression_matrix_raw.txt", index_col=0)
    barcodeDict = get_barcodeDict()
    expression_heatmap(geneList,barcodeDict)
