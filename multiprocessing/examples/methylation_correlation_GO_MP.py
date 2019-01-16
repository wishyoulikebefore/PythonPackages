# Created by zty on 2018/12/10
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
from scipy.stats import spearmanr
import argparse
import os
import glob
import matplotlib.pyplot as plt
import seaborn as sns
import multiprocessing

"""
usage:
-----------------------------------------------------------------------------------------------
update:
/root/mnt/Python-3.5.1/python /root/mnt/analysis/python_script/baidu_II/methylation_correlation_GO.py 
-f /root/mnt/analysis/baidu_II/RNAseq/normalized.csv 
-wd /root/mnt/analysis/baidu_II/WGBS_data 
-u 1
-g /root/mnt/analysis/baidu_II/PCA/GO_term_regulator/ensemble_annotation_regulator.genes 
-sd /root/mnt/analysis/baidu_II/PCA/GO_term_regulator

not update:
/root/mnt/Python-3.5.1/python /root/mnt/analysis/python_script/baidu_II/methylation_correlation_GO.py 
-f /root/mnt/analysis/baidu_II/RNAseq/normalized.csv 
-wd /root/mnt/analysis/baidu_II/WGBS_data 
-g /root/mnt/analysis/baidu_II/PCA/GO_term_regulator/ensemble_annotation_regulator.genes 
-sd /root/mnt/analysis/baidu_II/PCA/GO_term_regulator
"""

def parse_args():
    parser = argparse.ArgumentParser(description="methylated_gene_body")
    parser.add_argument("-f",help="normalized RNAseq")
    parser.add_argument("-wd",help="WGBS samples dir")
    parser.add_argument("-u",default=0,help="update RNAseq and WGBS")
    parser.add_argument("-g",help="target genes file")    #ENSE format
    parser.add_argument("-sd", help="save dir")
    args = parser.parse_args()
    return args.f,args.wd,args.u,args.g,args.sd

def global_methylation(file_suffix,title):
    sampleList = []
    PcgList = []
    for sample_id in glob.glob("*"):
        if os.path.isdir(sample_id):
            sample_id = os.path.basename(sample_id)
            gene_file = "%s/%s.%s" %(sample_id,sample_id,file_suffix)
            df = pd.read_table(gene_file, index_col=0)
            df["CG_Methy_loc"] = df.apply(lambda x: np.ceil(x["Total_covered_CG"] * x["CG_Methy_density"] / 100), axis=1)
            CG_methy_sum = df["CG_Methy_loc"].sum()
            Total_covered_CG_whole = df["Total_covered_CG"].sum()
            Pcg = CG_methy_sum / Total_covered_CG_whole
            sampleList.append(sample_id)
            PcgList.append(Pcg)
        else:
            pass
    glometh_df = pd.DataFrame(np.array(PcgList).reshape(-1,1),index=sampleList,columns=["Global Methylation"])
    glometh_df.to_csv("%s_global_methylation_level.csv" %(title))
    print("%s:%s处理完毕" %(title,file_suffix))

def correlation_analysis(matrix, normalized_rnaseq, geneList, name, sd):
    corrList = []
    for gene in geneList:
        try:
            expression_df = np.log2(normalized_rnaseq.loc[gene,:])
            matrix["Expression"] = expression_df
            matrix.dropna(how="all",inplace=True)
            matrix["Sample"] = np.where(matrix.index.str.contains("T"), "Tumor", "Normal")
            N_df = matrix[matrix["Sample"] == "Normal"]
            T_df = matrix[matrix["Sample"] == "Tumor"]
            N_df.fillna(0, inplace=True)
            T_df.fillna(0, inplace=True)
            N_corr, Np_value = spearmanr(N_df["Expression"], N_df["Global Methylation"])
            T_corr, Tp_value = spearmanr(T_df["Expression"], T_df["Global Methylation"])
            N_corr = round(N_corr, 4)
            T_corr = round(T_corr, 4)
            corrList.append([N_corr,T_corr])
            if np.abs(N_corr) >= 0.5 or np.abs(T_corr) >= 0.5:
                print("%s中%s结果值得注意：%s\t%s" %(name,gene,N_corr,T_corr))
        except KeyError:
            print("%s基因不在RNAseq中" %(gene))
    data = pd.DataFrame(corrList,index=geneList,columns=["N_corr","T_corr"])
    scatterplot(data, name, sd)
    data.to_csv("%s/Go_term_regulation_correlation_in_%s.csv" %(sd,name))

def scatterplot(data,name,sd,xmax=0.5,xmin=-0.5,ymax=0.5,ymin=-0.5):
    f, ax = plt.subplots(figsize=(8, 8))
    ax = sns.scatterplot(x="T_corr", y="N_corr", data=data)
    ax.hlines(y=0,xmin=xmin,xmax=xmax,colors="red",linestyles="dashed")
    ax.vlines(x=0, ymin=ymin, ymax=ymax, colors="red", linestyles="dashed")
    ax.set_xlabel("Regulator correlation in tumor",fontdict={"size":16,"weight":"bold"})
    ax.set_ylabel("Regulator correlation in normal", fontdict={"size":16,"weight":"bold"})
    ax.set_title(name,fontdict={"size":16,"weight":"bold"})
    ax.set(xlim=(xmin,xmax),ylim=(ymin,ymax))
    f.savefig("%s/%s_Go_term_scatterplot.png" %(sd,name),dpi=100,bbox_inches='tight')
    print("%s绘制完毕" %(name))

if __name__ == "__main__":
    rnaseq,WGBS_dir,update,gene_file,sd = parse_args()
    os.chdir(WGBS_dir)
    normalized_rnaseq = pd.read_csv(rnaseq, index_col=0)
    geneList = [i.rstrip() for i in open(gene_file)]

    if update:
        pool = multiprocessing.Pool(processes=3)
        pool.apply_async(global_methylation, args=("gene.filter.stat.all.xls", "gene",))
        pool.apply_async(global_methylation, args=("promoter.np1kb.filter.stat.all.xls", "np1kb_promoter",))
        pool.apply_async(global_methylation, args=("promoter.p2kb.filter.stat.all.xls", "p2kb_promoter",))
        pool.close()
        pool.join()

    glometh_list = {"gene_global_methylation_level.csv": "gene",
                    "np1kb_promoter_global_methylation_level.csv": "np1kb_promoter",
                    "p2kb_promoter_global_methylation_level.csv": "p2kb_promoter",
                    }
    normalized_rnaseq = normalized_rnaseq.loc[geneList,:].dropna(how="all")
    geneList = normalized_rnaseq.index.tolist()
    pool = multiprocessing.Pool(processes=3)
    for _file, name in glometh_list.items():
        matrix = pd.read_csv(_file, index_col=0)
        pool.apply_async(correlation_analysis, args=(matrix, normalized_rnaseq, geneList, name, sd,))
    pool.close()
    pool.join()
