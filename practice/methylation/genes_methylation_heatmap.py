# Created by zty on 2018/8/31
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns
import os
import time
from functools import wraps

"""
利用各甲基化位点计算出的score绘制heatmap

8.30：忘了把N和T分开(已解决)
      删除所有制相同的行(不应该)
      改为二进制文件（有无甲基化）
      
8.31 挑出N和T差异最大的1000个位点，看热力图有无明显区别
     速度优化：比较一下现在一个个join和一起concat的速度（将T和N输入列表中）以及先获取所有位点列表，直接填充
     
9.1  return dataframe时无法用timer计时，原因在于func(*args,**kwargs)
"""

def timer(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        start_time = time.time()
        func(*args,**kwargs)
        end_time = time.time()
        print("共耗时%s秒" % (end_time - start_time))
    return wrapper

@timer
def start():
    T_df = pd.DataFrame([])
    N_df = pd.DataFrame([])
    for CX_file in glob.glob("*CX_report.txt"):
        sample_name = CX_file.replace(".CX_report.txt", "")
        filter_df = process_sample(CX_file)
        if sample_name[-1] == "T":
            T_df = T_df.join(filter_df, how="outer")  # how="outer"
        elif sample_name[-1] == "N":
            N_df = N_df.join(filter_df, how="outer")
        else:
            pass
    T_sample = T_df.columns
    N_sample = N_df.columns
    meth_df = T_df.join(N_df,how="outer").fillna(0)
    meth_df.to_csv("CpG3_all.csv")
    meth_df = detect_difference(meth_df,T_sample,N_sample)
    meth_df.to_csv("CpG3_1000.csv")
    print("所有样本处理完毕")
    get_heatmap(meth_df)

#@timer
def process_sample(CX_file):
    start = time.time()
    sample_name = CX_file.replace(".CX_report.txt", "")
#    print("开始处理样本%s" %(sample_name))
    df = pd.read_table(CX_file,dtype={"chr": str, "loc": str, "meth": int, "unmeth": int, "minimum_counts(method1)": int})
    df["chr_loc"] = df["chr"] + "_" + df["loc"]
    df = df[(df["meth"] >= df["minimum_counts(method1)"]) & (df["type"] == "CG")]
    df[sample_name] = 1
    filter_df = df[["chr_loc", sample_name]]
    filter_df.set_index("chr_loc", inplace=True)
    end = time.time()
    print("样本%s 处理完毕，耗时%s秒" %(sample_name,round(end-start,2)))
    return filter_df

#@timer
def detect_difference(meth_df,T_sample,N_sample):
    print("开始提取差异最大的1000个位点")
    start = time.time()
    meth_df["T_mean"] = meth_df[T_sample].mean(axis=1)
    meth_df["N_mean"] = meth_df[N_sample].mean(axis=1)
    meth_df["diff"] = meth_df["T_mean"]-meth_df["N_mean"]   #meth_df["T_mean"]/meth_df["N_mean"]是否更好，防止分母为0
    meth_df = meth_df.sort_values(by="diff",ascending=False)
    filtered_df = pd.concat([meth_df[:500],meth_df[-500:]])
    end = time.time()
    print("差异最大的1000个位点提取完毕,共耗时%s秒" %(round(end-start,2)))
    return filtered_df.drop(["T_mean","N_mean","diff"],axis=1)

@timer
def get_heatmap(df):
    print("开始绘制热力图")
    f, ax = plt.subplots(figsize=(20, 15))
    sns.heatmap(df, cmap="BuPu", yticklabels=False)
    f.savefig('CpG3_1000.png', dpi=100, bbox_inches='tight')  # 保存的图片不会出现部分内容显示不全的现象
    print("热力图绘制完成")

if __name__ == "__main__":
    if os.path.exists("CpG3_1000.csv"):
        df = pd.read_csv("CpG3_1000.csv",index_col=0)
        get_heatmap(df)
    else:
        start()

