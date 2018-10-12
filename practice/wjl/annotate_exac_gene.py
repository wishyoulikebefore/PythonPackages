# Created by zty on 2018/10/12
import argparse
import os

"""
预先处理
le hg19_exac03nontcga.txt | awk '$9>0{print $1 "\t" $2 "\t" $3 "\t" $4 "\t" $5 "\t" $9}' > hg19_exac03nontcga_EAS.txt
le hg19_exac03.txt | awk '$9>0{print $1 "\t" $2 "\t" $3 "\t" $4 "\t" $5 "\t" $9}' > hg19_exac03_EAS.txt
le hg19_refGene.txt | awk '{print $3 "\t" $5 "\t" $6 "\t" $13}' > hg19_refGene_simplified.txt
耗时大约35min
"""

class pymongo():

    def __init__(self, timeout=300):
        self.timeout = timeout
        self.dict = dict()

    def update(self, gene, chr, start, end):
        if gene not in self.dict.keys():
            self.insert_one(gene)
            self.dict[gene]["gene"] = gene
            self.dict[gene]["chr"] = chr
            self.dict[gene]["start"] = start
            self.dict[gene]["end"] = end
        else:
            self.dict[gene]["start"] = min(self.dict[gene]["start"], start)
            self.dict[gene]["end"] = max(self.dict[gene]["end"], end)

    def insert_one(self, gene):
        self.dict[gene] = dict()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-ref")
    parser.add_argument("-f")
    parser.add_argument("-o")
    args = parser.parse_args()
    return args.ref,args.f,args.o

def process(refGene,exac_EAS,outName):
    mymongo = pymongo()
    output = open(outName, "a")
    output.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" %("Chr","Start","End","Ref","Alt","ExAC_nontcga_EAS","gene"))

    with open(refGene) as f:
        for line in f:
            lineList = line.rstrip().split("\t")
            chr = lineList[0].replace("chr", "")
            start = int(lineList[1])
            end = int(lineList[2])
            gene = lineList[3]
            mymongo.update(gene, chr, start, end)
    f.close()
    infoList = [mymongo.dict[key] for key in mymongo.dict]
    sortedList = sorted(infoList, key=lambda e: (e["chr"], e["start"]))

    def locate(chr, loc):
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
            gene = locate(chr,loc)
            if gene:
                output.write(line.rstrip()+"\t"+gene+"\n")
            else:
                output.write(line.rstrip() + "\t" + "gene_unknown" + "\n")
    f.close()

if __name__ == "__main__":
    refGene,exac_EAS,outName = parse_args()
    process(refGene,exac_EAS,outName)
