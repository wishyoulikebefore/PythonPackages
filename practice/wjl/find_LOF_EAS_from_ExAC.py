import argparse
import glob
import pandas as pd
import os

"""
从最起始的文件开始：hg19_exac03nontcga_EAS.txt + 下载的csv文件
基本思路：2)从下载的LOF.csv中提取出目标基因的LOF，需要进一步提取出EAS特有的LOF
          1)根据hg19_exac03nontcga_EAS.txt提取出EAS特有的chr和loc，处理上一步内容（组成列表，如chr_loc）
最好把基因注释也写上
          
"""

def get_LOF(_dir,locList,output):
    """
    合并各genes的LOF信息
    """
    os.chdir(_dir)
    df = pd.DataFrame([])
    for nu, csv in enumerate(glob.glob("*csv")):
        table = pd.read_csv(csv)
        table["gene"] = csv.replace(".csv","")
        df = df.append(table, ignore_index=True)
    df["loc"] = df.apply(lambda x:"%s_%s" %(x["Chrom"],x["Position"]),axis=1)
    df.set_index("loc",inplace=True)
    columns = df.columns
    filter_df = df.ix[locList].dropna(how="all")
    filter_df = filter_df.round({"Chrom":0,"Position":0})
    filter_df.set_index("gene",inplace=True)
    filter_df.to_csv(output,columns=columns)

def get_EAS(EAS_file):
    df = pd.read_table(EAS_file)
    df["loc"] = df.apply(lambda x:"%s_%s" %(x["Chr"],x["Start"]),axis=1)
    locList = df["loc"].unique().tolist()
    return locList

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", required=False, default=os.getcwd())
    parser.add_argument("EAS")
    parser.add_argument("csv_dir")
    parser.add_argument("-o", required=False, default="LOF_EAS.csv")
    args = parser.parse_args()
    os.chdir(args.d)
    locList = get_EAS(args.EAS)
    get_LOF(args.csv_dir,locList,args.o)



