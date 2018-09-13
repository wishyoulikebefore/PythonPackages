#2018-08-09 edit by zty
#modified in 2018-09-13
#作用：基于Seurat生成的表达矩阵检测某些基因在各cluster的表达情况
import pandas as pd
import os
import argparse
import glob
import re

"""
各簇某个基因是否表达：0-1
涉及文件的格式
------------------------------------------------------------------------------------------
cell_type.list：
0       Cytotoxic and partial exhausted CD8+
1       Activated CD8+
2       CD4+ resident memory

10XPIC_expression_matrix_raw.txt：
AAACCTGAGATACACA        AAACCTGCAATGGACG        AAACCTGGTCGAACAG        AAACCTGGTTCGTCTC        AAACCTGTCCCTCAGT        AAACCTGTCTGCAAG
RP11-34P13.7    0       0       0       0       0       0       0       0       0       0       0       0       0       0       0
FO538757.2      0       0       0       0       0       0       0       0       0       0       0       0       0       1       0
"""

output_expression = []

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
    clusters = []
    for file in glob.glob("cluster_barcode/*txt"):
        cluster_name = cell_typeDict.get(file.split("/")[-1].replace(".txt",""),"unrecognized")
        if cluster_name not in clusters:      #防止多个"unrecognized"
            clusters.append(cluster_name)
        for barcode in open(file).readlines():
            barcodeDict[barcode.strip()] = cluster_name
    barcodeSeries = pd.Series(barcodeDict)
    return  barcodeSeries,clusters

def process(geneList,clusters,expression_matrix,barcodeSeries,output_name):
    for gene in geneList:
        if "::" in gene:
            cal_multi_expression(gene,expression_matrix,clusters,barcodeSeries)
        else:
            cal_single_expression(gene,expression_matrix,clusters,barcodeSeries)
    output_df = pd.DataFrame(output_expression, index=geneList, columns=clusters)
    print("处理完毕")
    output_df.to_csv(output_name)

def fill(filter_cluster,clusters):
    uniq_clusterList = filter_cluster.unique().tolist()
    fillList = []
    for item in clusters:
        if item in uniq_clusterList:
            fillList.append(1)
        else:
            fillList.append(0)
    output_expression.append(fillList)

def cal_single_expression(gene,expression_matrix,clusters,barcodeSeries):
    #针对单个基因
    try:
        expression = expression_matrix.ix[gene]
    except:
        print("%s未检测到表达" % (gene))
        output_expression.append([0] * len(clusters))
        return
    filter_barcodes = expression[expression!=0].index
    filter_cluster = barcodeSeries.ix[filter_barcodes].dropna()           #获得表达特定基因barcode对应的clusters array
    fill(filter_cluster,clusters)

def cal_multi_expression(gene,expression_matrix,clusters,barcodeSeries):
    #针对多个基因杂合发挥作用的情况
    geneList = gene.split("::")
    try:
        expression = expression_matrix.ix[geneList]
    except:
        print("%s中部分基因未检测到表达" %(gene))
        output_expression.append([0] * len(clusters))
        return
    filter_barcodes = expression.ix[:,expression.all()].columns     #删除含有0的列，之前误写成any，所幸结果还未发出
    filter_cluster = barcodeSeries.ix[filter_barcodes].dropna()
    fill(filter_cluster,clusters)

if __name__ == "__main__":
    _dir, pro, genes = parse_args()
    geneList = [gene.strip().upper() for gene in open(genes).readlines()]
    os.chdir(os.path.join(_dir, pro))
    barcodeSeries, clusters = gen_temp_data(pro)
    expression_matrix = pd.read_table("%s_expression_matrix_raw.txt" %(pro), index_col=0)
    output_name = "%s_%s_cluster_gene_expression.csv" %(pro,re.sub("/.*/","",genes))
    process(geneList, clusters, expression_matrix, barcodeSeries, output_name)

"""
pandas用的还是不熟练，距离孔哥心中的“傻逼”还有好远的距离......
主要用到的技巧：选出1行数据中不为0的columns和多行数据中不出现0的列（利用any）；all和any注意区分
"""
