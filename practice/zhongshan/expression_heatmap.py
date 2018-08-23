# 2018-08-09 edit by zty
# 作用：基于Seurat生成的表达矩阵检测某些基因在各cluster的表达情况，定量，用于后续绘图
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import os
import argparse
import glob
import seaborn as sns
import os
import numpy as np

"""
UMI count使用log使颜色层次化
对于0或NA值，以1替代，log2值为0
"""

sns.set(rc={'figure.figsize':(10,10)})

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
        UMI_sum =np.log2(expression[value].sum(axis=1).replace(0,1))
        UMI_countList.append(UMI_sum)
    UMIs = pd.DataFrame(UMI_countList,index=barcodeDict.keys(),columns=geneList)
    sns_fig = sns.heatmap(UMIs,annot=True,cmap="BuPu",linewidths=0.5)
    sns_fig.figure.savefig('heatmap.png')

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
