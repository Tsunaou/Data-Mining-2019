# python3
# -*- coding: utf-8 -*-
# @Author  : lina
# @Time    : 2018/5/13 11:40
import fp_growth_py3 as fpg
import time
from FileOption import  FileOption
from Apriori import generateRules


if __name__ == '__main__':

    '''
    调用find_frequent_itemsets()生成频繁项
    @:param minimum_support表示设置的最小支持度，即若支持度大于等于inimum_support，保存此频繁项，否则删除
    @:param include_support表示返回结果是否包含支持度，若include_support=True，返回结果中包含itemset和support，否则只返回itemset
    '''

    start = time.time()  # 计算程序运行时间


    fop = FileOption()
    dataset= fop.get_data_FP_new('dataset/Groceries.csv')
    minSup = dataset.__len__() * 0.02
    minConf = 0.02

    frequent_itemsets = fpg.find_frequent_itemsets(dataset, minimum_support=minSup, include_support=True)
    print(type(frequent_itemsets))   # print type

    result = []
    for itemset, support in frequent_itemsets:    # 将generator结果存入list
        result.append((itemset, support))

    result = sorted(result, key=lambda i: i[0])   # 排序后输出
    for itemset, support in result:
        print(str(itemset) + ' ' + str(support/dataset.__len__()))
    print("频繁项集个数",result.__len__())


    L = []
    L.append([])
    supportData = {}
    for itemset, support in result:
        itlen = itemset.__len__()
        if itlen == 1:
            L[0].append(frozenset(itemset))
        else:
            if L.__len__() >= itlen:
                L[itlen-1].append(frozenset(itemset))
            else:
                while(L.__len__() < itlen):
                    L.append([])
                L[itlen - 1].append(frozenset(itemset))
        supportData[frozenset(itemset)] = support/dataset.__len__()


    rules = generateRules(L, supportData, minConf=minConf)

    newRule = []
    for rule in rules:
        newRule.append((list(set(rule[0])),list(set(rule[1])),rule[2]))
        # rule[0] = list(rule[0])
        # rule[1] = list(rule[1])
    print("一共有"+str(rules.__len__())+"条满足置信度的规则，如下所示")

    newRule = sorted(newRule, key=lambda i: i[0])   # 排序后输出
    for rule in newRule:
        print(str(rule[0])+"->"+str(rule[1])+":"+str(rule[2]))
    # for rule in rules:
    #     print(str(list(rule[0]))+"->"+str(list(rule[1]))+":"+str(rule[2]))
    end = time.time()
    print("运行时间：" + str(end - start) + "s")


