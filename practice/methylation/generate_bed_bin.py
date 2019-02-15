# Created by zty on 2018/12/21
import argparse
import glob
import subprocess
import numpy as np

def parse_args():
    parser = argparse.ArgumentParser(description="split bed file")
    parser.add_argument("-f",help="bed file")
    parser.add_argument("-m",choices={"bins","binsize"},help="split based on binsize")
    parser.add_argument("-p",help="parameter")
    args = parser.parse_args()
    return args.f,args.m,args.p

def split1(_file,binsize):
    """
    binsize
    """
    output = open("%sbp_%s" %(binsize,_file),"a")
    binsize = int(binsize)
    with open(_file) as f:
        for line in f:
            lineList = line.rstrip().split()
            chr = lineList[0]
            start = int(lineList[1])
            end = int(lineList[2])
            gene = lineList[3]
            chain = lineList[4]
            ensemble = lineList[5]
            a,b = np.divmod(end-start+1,binsize)    # a = bins ; b = remain
            a = int(a)
            b = int(b)
            if chain == "+":
                for bin in range(1,a+1):
                    output.write("%s\t%s\t%s\t%s\t%s\t%s_%s%s\n" %(chr,start,start+binsize-1,gene,chain,ensemble,"bin",bin))
                    start += binsize
                if b != 0:
                    output.write("%s\t%s\t%s\t%s\t%s\t%s_%s%s\n" %(chr,start,end,gene,chain,ensemble,"bin",a+1))
            elif chain == "-":
                for bin in range(1,a+1):
                    output.write("%s\t%s\t%s\t%s\t%s\t%s_%s%s\n" % (chr, end-binsize+1, end, gene, chain, ensemble, "bin", bin))
                    end -= binsize
                if b != 0:
                    output.write("%s\t%s\t%s\t%s\t%s\t%s_%s%s\n" % (chr, start, end, gene, chain, ensemble, "bin", a + 1))
        output.close()

def split2(_file,bins):
    """
    bins
    """
    output = open("%sbins_%s" %(bins,_file),"a")
    bins = int(bins)
    with open(_file) as f:
        for line in f:
            lineList = line.rstrip().split()
            chr = lineList[0]
            start = int(lineList[1])
            end = int(lineList[2])
            gene = lineList[3]
            chain = lineList[4]
            ensemble = lineList[5]
            a,b = np.divmod(end-start+1,bins)    # a=binsize ; b = remain
            a = int(a)
            b = int(b)
            if a == 0:     #gene length < 100 ,such as CDR3 related genes
                pass
            else:
                if chain == "+":
                    for bin in range(1,b+1):  # divide value b equally
                        output.write("%s\t%s\t%s\t%s\t%s\t%s_%s%s\n" %(chr,start,start+a,gene,chain,ensemble,"bin",bin))
                        start += (a+1)
                    for bin in range(b+1,bins+1):
                        output.write("%s\t%s\t%s\t%s\t%s\t%s_%s%s\n" %(chr,start,start+a-1,gene,chain,ensemble,"bin",bin))
                        start += a
                elif chain == "-":
                    for bin in range(1,b+1):
                        output.write("%s\t%s\t%s\t%s\t%s\t%s_%s%s\n" % (chr, end-a, end, gene, chain, ensemble, "bin", bin))
                        end -= (a+1)
                    for bin in range(b+1,bins+1):
                        output.write("%s\t%s\t%s\t%s\t%s\t%s_%s%s\n" %(chr,end-a+1,end,gene,chain,ensemble,"bin",bin))
                        end -= a
        output.close()

if __name__ == "__main__":
    _file, mode, parameter = parse_args()
    if mode == "binsize":
        split1(_file, parameter)
    else:
        split2(_file, parameter)
