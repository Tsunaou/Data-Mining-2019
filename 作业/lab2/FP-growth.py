from fp_growth_py3 import find_frequent_itemsets
from FileOption import  FileOption
from Apriori import generateRules
import time


def FP_rule_adapter(result):
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
        supportData[frozenset(itemset)] = support / dataset.__len__()
    return  L,supportData


if __name__ == '__main__':

    start = time.time()  # 计算程序运行时间

    fop = FileOption()
    # dataset= fop.get_data_FP_new('dataset/Groceries.csv')
    # dataset= fop.get_data_FP_new('dataset/testfp.csv')
    dataset = fop.get_data_FP_UNIX()
    minSup = dataset.__len__() * 0.01
    minConf = 0.01

    frequent_itemsets = find_frequent_itemsets(dataset, minSup=minSup)
    print(type(frequent_itemsets))   # print type

    result = []
    for itemset, support in frequent_itemsets:    # 将generator结果存入list
        result.append((itemset, support))

    result = sorted(result, key=lambda i: i[0])   # 排序后输出
    for itemset, support in result:
        print(str(itemset) + ' ' + str(support/dataset.__len__()))
    print("频繁项集个数",result.__len__())

    L, supportData = FP_rule_adapter(result=result)

    rules = generateRules(L, supportData, minConf=minConf)

    for rule in rules:
        print(str(rule[0])+"->"+str(rule[1])+":"+str(rule[2]))

    end = time.time()
    print("频繁项集个数",result.__len__())
    print("挖掘到规则数",rules.__len__())

    print("运行时间：" + str(end - start) + "s")


