# Created by zty on 2018/9/25
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import  matplotlib.pyplot as plt
import argparse
import numpy as np
import seaborn as sns

"""
KEGGID  Pvalue  OddsRatio       ExpCount        Count   Size    Term    FDR     GeneSymbol
05322   2.57191543855093e-35    10.8899762209621        13.153726975383 69      135     Systemic lupus erythematosus    5.2467074946439e-33     HIST2H3C, HIST1H2AI, HIST1H2BO, HIST1H3C, HIST1H2BM, HIST1H3B, HIST1H2AL, HIST1H2AG, HIST1H2AH, HIST1H2BL, HIST1H2AM, HIST1H3G, HIST1H3J, HIST1H2BI, HIST1H2BH, IFNG, HIST1H2AB, HIST1H2BF, HIST1H3H, HIST1H2BB, HLA-DOB, HIST3H2BB, HIST1H2BJ, HIST1H3F, HIST1H2BE, HIST1H3I, HIST1H3D, HIST1H2BD, HIST1H2BG, FCGR3A, HIST1H4L, HIST2H3D, C1QC, C2, HLA-DQA1, HIST2H2AA3, HIST2H2BF, HIST1H2AK, CD28, HIST1H2AD, HIST1H2BN, HIST1H4A, FCGR2C, HLA-DQB1, H2AFX, HIST2H4A, C1QB, HIST1H4I, C1R, HLA-DOA, HLA-DQA2, HIST1H4J, HLA-DMB, FCGR1A, HIST1H2BC, C4B, C1QA, HLA-DPB1, HIST1H4D, HIST1H4K, C3, CD80, HIST1H2AE, C4A, CD86, HIST1H2BK, HIST2H2BE, HIST3H2A, HIST1H4F
04060   3.71229441423678e-11    3.01442015488678        25.6254088483388        61      263     Cytokine-cytokine receptor interaction  3.78654030252151e-09    CXCL9, CXCL13, CXCL10, CXCL11, IL2RA, CCL13, CXCL14, CCL18, CCL19, CLCF1, CCL8, IL21R, IFNG, CD27, CCR8, TNFRSF9, CCR7, TNFSF4, OSM, CXCR6, IL2RB, TNFRSF21, IFNE, CCL5, TNFRSF6B, CCR4, CCL3L1, CD70, FASLG, LTB, EGF, CCR5, CCL22, CSF1R, TNFRSF18, TNFSF13B, CXCR3, IL9R, CXCR5, TNFSF11, IL22RA2, CCL4, CCR1, CCL3, CCR6, CCL3L3, CSF2, TNFSF15, IL2RG, TNFRSF17, CCL4L1, CCR2, IL12RB2, CCL21, TNFSF8, IL12B, FLT3, LTA, XCR1, CCL17, IL24
04514   1.71076399050849e-09    3.74998030875866        12.9588569461181        37      133     Cell adhesion molecules (CAMs)  1.16331951354577e-07    CDH3, CTLA4, HLA-DOB, SDC3, CD8A, HLA-G, ICOS, CLDN1, CLDN4, HLA-DQA1, CD8B, CD6, VCAN, CD28, CD2, CDH2, CD274, HLA-DQB1, NLGN4X, HLA-A, NECTIN1, HLA-DOA, HLA-DQA2, SIGLEC1, HLA-DMB, PDCD1, ITGB7, VCAM1, CDH1, CLDN2, HLA-DPB1, CD80, HLA-B, CD86, PDCD1LG2, L1CAM, CNTNAP2
04940   3.89158544089326e-09    7.5533973187081 4.18970562919607        19      43      Type I diabetes mellitus        1.98470857485556e-07    IFNG, GZMB, HLA-DOB, HLA-G, FASLG, HLA-DQA1, CD28, HLA-DQB1, HLA-A, HLA-DOA, HLA-DQA2, HLA-DMB, HLA-DPB1, CD80, HLA-B, CD86, IL12B, GAD1, LTA

涉及指标
横坐标：Rich Factor (count/size)
纵坐标：Pathway Name (Term)
颜色：-log10(Pvalue)
大小：gene number (GeneSymbol中的个数)  df.str.count(",")+1
"""

def bubble(KEGG_file):
    df = pd.read_table(KEGG_file,index_col=0)
    df["rich_factor"] = df["Count"]/df["Size"]
    df["-log10(Pvalue)"] = -np.log10(df["Pvalue"])
    df["Gene Number"] = df["GeneSymbol"].str.count(",")+1
    f, ax = plt.subplots(figsize=(6, 8))
    cmap = sns.cubehelix_palette(dark=.3, light=.8, as_cmap=True)
    sns.scatterplot(x="rich_factor",y="Term",hue="-log10(Pvalue)",size="Gene Number",palette="RdYlGn",data=df)
    ax.set_xlabel("Rich factor")
    ax.set_ylabel("Pathway Name")
    ax.set_title("Statistics of Pathway Enrichment")
    f.savefig('bubble.pdf', dpi=100, bbox_inches='tight')

if __name__ == "__main__":
    bubble("DEG_R18037376LR02-F261T_vs_R18037374LR01-F261N_sig_up_gene_list_KEGG.xls")
