import pandas as pd
import numpy as np
import time

class FileOption:

    dataset_original = []  # 初始读入的数据
    items = []  # 数据集中项的种类
    transactions = []   # 数据集

    def load_csv(self,filename):
        df = pd.read_csv(filename)  # 这个会直接默认读取到这个Excel的第一个表单
        data = np.array(df.loc[:, :])  # 主要数据，包含统计值
        data = data[:,1]
        self.dataset_original = data

    def get_frozenset(self,filename):
        self.load_csv(filename)
        out = []
        for lines in self.dataset_original:
            lines = str(lines)
            # print("before:"+lines)
            lines = lines.strip('{}')  # 去除两端的符号
            lines = lines.replace('/', ' ')  # 把斜杠转化为空格
            # print("after :"+lines)
            transaction = lines.split(',')
            self.transactions.append(transaction)
            for item in transaction:
                if not [item] in out:
                    out.append([item])
        out.sort()
        self.transactions = list(map(set, self.transactions))
        # 使用frozenset是为了后面可以将这些值作为字典的键
        self.items = list(map(frozenset, out))  # frozenset一种不可变的集合，set可变集合


    def get_data(self,filename):
        self.get_frozenset(filename=filename)
        return self.items, self.transactions


def scanD(dataset, Ck, minSupport):
    """
    将不符合minSupport的集合删去，
    返回频繁项集列表:retList 所有元素的支持度Dict:supportData
    """
    ssCnt = {}
    for tid in dataset:
        for can in Ck:
            if can.issubset(tid):  # 判断can是否是tid的子集
                if can not in ssCnt:  # 统计该值在整个记录中满足子集的次数（以字典的形式记录，frozenset为键）
                    ssCnt[can] = 1
                else:
                    ssCnt[can] += 1
    numItems = dataset.__len__()
    retList = []  # 重新记录满足条件的数据值（即支持度大于阈值的数据）
    supportData = {}  # 每个数据值的支持度
    for key in ssCnt:
        support = ssCnt[key] / numItems
        if support >= minSupport:
            retList.insert(0, key)
        supportData[key] = support
    return retList, supportData


def aprioriGen(Lk, k):
    """
    当前k-2项相同时，将两个集合合并
    返回频繁项集列表Ck:retList
    """
    retList = []
    lenLk = Lk.__len__()
    for i in range(lenLk):  # 两层循环比较Lk中的每个元素与其它元素
        for j in range(i + 1, lenLk):
            L1 = list(Lk[i])[0:k - 2]  # 将集合转为list后取值
            L2 = list(Lk[j])[0:k - 2]
            L1.sort()
            L2.sort()
            if L1 == L2:
                res = Lk[i] | Lk[j]
                retList.append(res)  # 求并集
    return retList

def apriori(items,transactions, minSupport=0.5):
    """
    返回 所有满足大于阈值的组合 集合支持度列表
    """
    L1, supportData = scanD(transactions, items, minSupport)  # 过滤数据,得到的L1列表中的每个单项至少出现在满足minSupport的记录中
    L = [L1]
    k = 2
    while (len(L[k - 2]) > 0):  # 若仍有满足支持度的集合则继续做关联分析
        Ck = aprioriGen(L[k - 2], k)  # Ck候选频繁项集
        Lk, supK = scanD(transactions, Ck, minSupport)  # Lk频繁项集
        supportData.update(supK)  # 更新字典（把新出现的集合:支持度加入到supportData中）
        L.append(Lk)
        k = k + 1  # 每次新组合的元素都只增加了一个，所以k也+1（k表示元素个数）
    return L, supportData

def generateRules(L, supportData, minConf=0.7):  # supportData 是一个字典
    """
    返回 满足最小置信度的规则列表:bigRuleList
    """
    bigRuleList = []
    for i in range(1, len(L)):  # 从为2个元素的集合开始
        for freqSet in L[i]:
            # 只包含单个元素的集合列表
            H1 = [frozenset([item]) for item in freqSet]  # frozenset({2, 3}) 转换为 [frozenset({2}), frozenset({3})]
            # 如果集合元素大于2个，则需要处理才能获得规则
            if (i > 1):
                rulesFromConseq(freqSet, H1, supportData, bigRuleList, minConf)  # 集合元素 集合拆分后的列表 。。。
            else:
                calcConf(freqSet, H1, supportData, bigRuleList, minConf)
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

if __name__ == '__main__':

    start = time.time()  # 计算程序运行时间

    fop = FileOption()
    items, transactions = fop.get_data('dataset/Groceries.csv')
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
        for its in Li:
            print( str(its) + "->" + str(supportData.get(its)))  # 输出每个频繁项集的支持度
    print("频繁项数为："+str(count))
    rules = generateRules(L, supportData, minConf=minConf)
    print("一共有"+str(rules.__len__())+"条满足置信度的规则，如下所示")
    for rule in rules:
        print(str(rule[0])+"->"+str(rule[1])+":"+str(rule[2]))

    end = time.time()
    print("运行时间：" + str(end - start) + "s")

