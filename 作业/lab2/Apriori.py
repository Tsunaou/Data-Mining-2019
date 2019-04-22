import time
from FileOption import FileOption
from collections import defaultdict

def scanD(dataset, Ck, minSupport):
    """
    将不符合minSupport的集合删去，
    返回频繁项集列表:retList 所有元素的支持度Dict:supportData
    """
    ssCnt = defaultdict(lambda: 0) # 默认值为0的字典
    for trans in dataset:
        for item in Ck:
            # 判断can是否是tid的子集，并以此计算sup_count
            if item.issubset(trans):
                ssCnt[item] += 1

    dataLenth = dataset.__len__()

    retList = []  # 重新记录每一项的值
    supportData = {}  # 项的支持度

    for item in ssCnt:
        support = ssCnt[item] / dataLenth
        # 保留满足最小支持度要求的项
        if support >= minSupport:
            retList.append(item)
        supportData[item] = support

    return retList, supportData


def aprioriGen(Lk, k):
    """
    当前k-2项相同时，将两个集合合并
    返回频繁项集列表Ck:res
    """
    resList = []
    for i in range(Lk.__len__()):  # 两层循环比较Lk中的每个元素与其它元素
        for j in range(i + 1, Lk.__len__()):
            L1 = (list(Lk[i])[0:k - 2]).sort()  # 取集合排序后的前k-1项
            L2 = (list(Lk[j])[0:k - 2]).sort()
            if L1 == L2:
                # 比较前k-1项，若前k-1项相同，则合并
                res = Lk[i] | Lk[j]
                resList.append(res)  # 求并集
    return resList

def apriori(items,transactions, minSupport=0.5):
    """
    返回 所有满足大于阈值的组合 集合支持度列表
    """
    L1, supportData = scanD(transactions, items, minSupport)  # 过滤数据,得到的L1列表中的每个单项至少出现在满足minSupport的记录中
    L = []  # 记录频繁项
    L.append(L1)
    k = 2
    while len(L[k - 2]) > 0:  # 若仍有满足支持度的集合则继续做关联分析
        Ck = aprioriGen(L[k - 2], k)  # Ck候选频繁项集
        Lk, supK = scanD(transactions, Ck, minSupport)  # Lk频繁项集
        supportData.update(supK)  # 把新出现的(trans:support)加入到supportData中
        L.append(Lk)
        k = k + 1
    return L, supportData


def generateRules(L, supportData, minConf=0.7):  # supportData 是一个字典
    """
    返回 满足最小置信度的规则列表:newRule
    """
    bigRuleList = []
    for i in range(1, len(L)):  # 只获取有至少两个元素的集合
        for freqSet in L[i]:
            # 转化为只包含单个元素的集合列表
            H1 = [frozenset([item]) for item in freqSet]  # frozenset({2, 3}) 转换为 [frozenset({2}), frozenset({3})]


            if i > 1:
                # 如果集合元素大于2个，则需要处理才能获得规则
                rulesFromConseq(freqSet, H1, supportData, bigRuleList, minConf)
            else:
                calcConf(freqSet, H1, supportData, bigRuleList, minConf)

    # 对生成的rule排序,以便观察
    # newRule = []
    # for rule in bigRuleList:
    #     newRule.append((list(set(rule[0])),list(set(rule[1])),rule[2]))
    # newRule = sorted(newRule, key=lambda i: i[0])   # 排序

    return bigRuleList


def calcConf(freqSet, H, supportData, brl, minConf=0.7):
    """
    对规则进行评估
    返回 满足最小可信度的关联规则:prunedH
    """
    prunedH = []  # 创建一个新的列表去返回
    for conseq in H:
        conf = supportData.get(freqSet) / supportData.get(freqSet - conseq)
        if conf >= minConf:
            brl.append((freqSet - conseq, conseq, conf))
            prunedH.append(conseq)
    return prunedH


# 生成候选规则集合
def rulesFromConseq(freqSet, H, supportData, brl, minConf=0.7):
    m = H[0].__len__()
    if (len(freqSet) > (m + 1)):  # 尝试进一步合并
        Hmp1 = aprioriGen(H, m + 1)  # 将单个集合元素两两合并
        Hmp1 = calcConf(freqSet, Hmp1, supportData, brl, minConf)
        if (len(Hmp1) > 1):  # need at least two sets to merge
            rulesFromConseq(freqSet, Hmp1, supportData, brl, minConf)

def getApriori(datatype=0,minSup=0.5,minConf=0.7,getFreqitems=True,getRules=False):
    '''
    使用 Apriori算法得到频繁项集和规则
    :param datatype: 挖掘的数据集，0为Groceies数据集，1为UNIX数据集, 2为测试暴力算法测试集
    :param getFreqitems: 是否得到频繁项
    :param getRules: 是否得到频繁规则
    :return:
    '''

    fop = FileOption()
    items = []
    transactions = []

    if datatype == 0:
        items, transactions = fop.get_data('dataset/Groceries.csv')
    elif datatype == 1:
        items, transactions = fop.get_UNIX_data()
    elif datatype == 2:
        items, transactions = fop.get_data('dataset/bftest.csv')
    else:
        print("数据集类型出错")
        return

    minSupport = minSup
    minConf = minConf

    print("Apriori 开始")
    L, supportData = apriori(items, transactions, minSupport=minSupport)

    count = 0  # 频繁项集数
    if getFreqitems:
        for Li in L:
            count += Li.__len__()
            Llist = []
            for items in Li:
                Llist.append(list(set(items)))
            result = sorted(Llist, key=lambda i: i[0])  # 排序后输出
            for its in result:
                print(str(its) + "->" + str(supportData.get(frozenset(its))))  # 输出每个频繁项集的支持度
    print("频繁项数为："+str(count))

    rules = generateRules(L, supportData, minConf=minConf)
    if getRules:
        print("一共有" + str(rules.__len__()) + "条满足置信度的规则，如下所示")
        for rule in rules:
            print(str(rule[0]) + "->" + str(rule[1]) + ":" + str(rule[2]))


    print("频繁项集个数", count)
    print("挖掘到规则数", rules.__len__())





if __name__ == '__main__':

    start = time.time()  # 计算程序运行时间

    fop = FileOption()
    items, transactions = fop.get_data('dataset/Groceries.csv')
    # items, transactions = fop.get_data('dataset/testbf.csv')
    # items, transactions = fop.get_UNIX_data()

    minSupport = 0.05
    minConf = 0.05
    print("最小支持度为："+str(minSupport))
    print("最小置信度为："+str(minConf))
    print("Apriori 开始")
    L, supportData = apriori(items,transactions,minSupport=minSupport)
    print("Apriori 结束，频繁项集如下")
    count = 0  # 频繁项集数
    for Li in L:
        count += Li.__len__()
        Llist = []
        for items in Li:
            Llist.append(list(set(items)))
        result = sorted(Llist, key=lambda i: i[0])  # 排序后输出
        for its in result:
            print( str(its) + "->" + str(supportData.get(frozenset(its))))  # 输出每个频繁项集的支持度
    print("频繁项数为："+str(count))

    rules = generateRules(L, supportData, minConf=minConf)

    print("一共有"+str(rules.__len__())+"条满足置信度的规则，如下所示")

    for rule in rules:
        print(str(rule[0])+"->"+str(rule[1])+":"+str(rule[2]))

    print("频繁项数为："+str(count))
    print("一共有"+str(rules.__len__())+"条满足置信度的规则，如下所示")

    end = time.time()
    print("运行时间：" + str(end - start) + "s")

