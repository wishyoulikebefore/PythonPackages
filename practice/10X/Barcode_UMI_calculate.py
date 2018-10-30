# Created by zty on 2018/10/30
import pandas as pd
import argparse
import gzip
import glob
import os
import multiprocessing

"""
查看R1和R2 barcode和UMI的组成是否相似
"""

def parse_args():
    parser = argparse.ArgumentParser(description="统计10X VDJ测序数据中barcode和UMI")
    parser.add_argument("-d", help="提取文件路径")
    args = parser.parse_args()
    return args.d

def process_fastq(R1_file,R2_file,save_name):
    data = []
    with gzip.open(R1_file) as f:
        for nu,line in enumerate(f):
            if nu%4 == 1:
                line = line.rstrip()
                barcode = line[:16]
                umi = line[16:26]
                data.append([barcode,umi,"R1"])
            else:
                pass
    f.close()
    with gzip.open(R2_file) as f:
        for nu,line in enumerate(f):
            if nu%4 == 1:
                line = line.rstrip()
                barcode = line[:16]
                umi = line[16:26]
                data.append([barcode,umi,"R2"])
            else:
                pass
    f.close()
    df = pd.DataFrame(data,columns=["Barcode","UMI"])
    df.to_csv(save_name,index=False)

if __name__ == "__main__":
    _dir = parse_args()
    pool = multiprocessing.Pool(processes=8)
    os.chdir(_dir)
    for sample_dir in glob.glob("Sample_*"):
        R1_file = glob.glob("%s/*_R1.fastq.gz" %(sample_dir))[0]
        R2_file = glob.glob("%s/*_R2.fastq.gz" %(sample_dir))[0]
        save_name = "%s_barcode_umi_calculate.csv" %(sample_dir)
        pool.apply_async(process_fastq, args=(R1_file,R2_file,save_name,))
    pool.close()
    pool.join()
