import argparse
import os

"""
获取目标基因在ExAC EAS中出现的所有突变（并非都是LOF突变）
"""

os.chdir("/glusterfs/home/zuo_tianyu/database/exac03")

parser = argparse.ArgumentParser()
parser.add_argument("gene_file")
parser.add_argument("EAS")
parser.add_argument("output")
args = parser.parse_args()

refGene = "simplified_refGene.txt"
targetGene = args.gene_file
exac_EAS = args.EAS
output = open(args.output,"a")

target_geneList = [i.rstrip() for i in open(targetGene).readlines()]

class pymongo():

        def __init__(self,timeout=300):
            self.timeout = timeout
            self.dict = dict()

        def update(self,gene,chr,start,end):
            if gene not in self.dict.keys():
                self.insert_one(gene)
                self.dict[gene]["gene"] = gene
                self.dict[gene]["chr"] = chr
                self.dict[gene]["start"] = start
                self.dict[gene]["end"] = end
            else:
                self.dict[gene]["start"] = min(self.dict[gene]["start"], start)
                self.dict[gene]["end"] = max(self.dict[gene]["end"], end)

        def insert_one(self,gene):
            self.dict[gene] = dict()

mymongo = pymongo()
with open(refGene) as f:
    for line in f.readlines():
        lineList = line.rstrip().split("\t")
        chr = lineList[0].replace("chr","")
        start = int(lineList[1])
        end = int(lineList[2])
        gene = lineList[3]
        if gene in target_geneList:
            mymongo.update(gene,chr,start,end)
        else:
            pass
f.close()

infoList = [mymongo.dict[key] for key in mymongo.dict]
sortedList = sorted(infoList,key = lambda e:(e["chr"],e["start"]))

def judge(chr,loc):
    for item in sortedList:
        if chr == item["chr"] and loc >= item["start"] and loc <= item["end"]:
            return item["gene"]
        else:
            pass
    return

with open(exac_EAS) as f:
    for line in f.readlines()[1:]:
        lineList = line.rstrip().split("\t")
        chr = lineList[0]
        loc = int(lineList[1])
        this_judge = judge(chr,loc)
        if this_judge:
            output.write(line.rstrip()+"\t"+this_judge+"\n")
        else:
            pass
f.close()

#总结
"""
没有pymongo，所以要自己模仿pymongo写个类
主要用到的技巧：数据文件的前期简化；搜索前的排序（如字典多keys的排序）
"""


