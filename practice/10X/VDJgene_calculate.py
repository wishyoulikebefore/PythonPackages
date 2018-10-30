# Created by zty on 2018/10/29
import pandas as pd
import sys
import argparse

"""
提取数据至dataframe
根据classification和cover_region统计平均长度
"""

def parse_args():
    parser = argparse.ArgumentParser(description="统计VDJ基因亚型")
    parser.add_argument("-f", help="regions.fa")
    args = parser.parse_args()
    return args.f

def pre_process(_file):
    data = []
    f = open(_file).readlines()
    for nu,line in enumerate(f):
        if nu % 2 == 1:
            pass
        else:
            lineList = line.rstrip().split("|")
            subtype = lineList[2]
            cover_region = lineList[3]    #排除C-REGION
            classification = lineList[4]
            chain = lineList[5]
            aa = f[nu+1].rstrip()
            data.append([subtype,classification,cover_region,chain,aa])
    df = pd.DataFrame(data,columns=["subtype","classification","cover_region","chain","aa"])
    df.set_index("subtype",inplace=True)
    df["length"] = df.apply(lambda x:len(x["aa"]),axis=1)
    df.sort_values(by=["chain","subtype","length"],inplace=True)
    df = df[df["cover_region"]!="C-REGION"]
    df.to_csv("VDJgenes_calculation.csv")
    return df

def calculate(df):
    pivot_df = df.pivot_table(values="length",index=["classification","chain"],columns=["cover_region"])
    pivot_df = pivot_df.round(decimals=1)
    pivot_df.to_csv("VDJ_pivot_table.csv")


if __name__ == "__main__":
    _file = parse_args()
    df = pre_process(_file)
    calculate(df)
