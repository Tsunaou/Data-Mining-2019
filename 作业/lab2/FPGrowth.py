from fp_growth_py3 import find_frequent_itemsets
from FileOption import  FileOption
from Apriori import generateRules
import time


def FP_rule_adapter(result,datasetlenth):
    L = []
    L.append([])
    supportData = {}
    for itemset, support in result:
        itlen = itemset.__len__()
        if itlen == 1:
            L[0].append(frozenset(itemset))
        else:
            if L.__len__() >= itlen:
                L[itlen - 1].append(frozenset(itemset))
            else:
                while (L.__len__() < itlen):
                    L.append([])
                L[itlen - 1].append(frozenset(itemset))
        supportData[frozenset(itemset)] = support / datasetlenth
    return  L,supportData

def getFPGrowth(datatype=0,minSup=0.5,minConf=0.7,getFreqitems=True,getRules=False):
    '''
    使用 FPGrowth算法得到频繁项集和规则
    :param datatype: 挖掘的数据集，0为Groceies数据集，1为UNIX数据集, 2为测试暴力算法测试集
    :param getFreqitems: 是否得到频繁项
    :param getFreqitems: 是否得到频繁项
    :param getRules: 是否得到频繁规则
    :return:
    '''

    fop = FileOption()
    dataset = []
    if datatype == 0:
        dataset= fop.get_data_FP_new('dataset/Groceries.csv')
    elif datatype == 1:
        dataset = fop.get_data_FP_UNIX()
    elif datatype == 2:
        dataset = fop.get_data_FP_new('dataset/testbf.csv')
    else:
        print("数据集类型出错")
        return
    minSupport = dataset.__len__() * minSup
    minConf = minConf

    print("FP-Growth 开始")
    frequent_itemsets = find_frequent_itemsets(dataset, minSup=minSupport)
    # print(type(frequent_itemsets))   # print type

    result = []
    for itemset, support in frequent_itemsets:    # 将generator结果存入list
        result.append((itemset, support))

    result = sorted(result, key=lambda i: i[0])   # 排序后输出
    if getFreqitems:
        for itemset, support in result:
            print(str(itemset) + ' ' + str(support/dataset.__len__()))
    print("频繁项集个数",result.__len__())

    L, supportData = FP_rule_adapter(result=result,datasetlenth=dataset.__len__())

    rules = generateRules(L, supportData, minConf=minConf)

    if getRules:
        for rule in rules:
            print(str(rule[0]) + "->" + str(rule[1]) + ":" + str(rule[2]))

    print("频繁项集个数", result.__len__())
    print("挖掘到规则数", rules.__len__())


if __name__ == '__main__':

    start = time.time()  # 计算程序运行时间

    fop = FileOption()
    # dataset= fop.get_data_FP_new('dataset/Groceries.csv')
    # dataset= fop.get_data_FP_new('dataset/testbf.csv')
    dataset = fop.get_data_FP_UNIX()
    minSup = dataset.__len__() * 0.01
    minConf = 0.01

    frequent_itemsets = find_frequent_itemsets(dataset, minSup=minSup)
    # print(type(frequent_itemsets))   # print type

    result = []
    for itemset, support in frequent_itemsets:    # 将generator结果存入list
        result.append((itemset, support))

    result = sorted(result, key=lambda i: i[0])   # 排序后输出
    for itemset, support in result:
        print(str(itemset) + ' ' + str(support/dataset.__len__()))
    print("频繁项集个数",result.__len__())

    L, supportData = FP_rule_adapter(result=result,datasetlenth=dataset.__len__())

    rules = generateRules(L, supportData, minConf=minConf)

    for rule in rules:
        print(str(rule[0])+"->"+str(rule[1])+":"+str(rule[2]))

    end = time.time()
    print("频繁项集个数",result.__len__())
    print("挖掘到规则数",rules.__len__())

    print("运行时间：" + str(end - start) + "s")


