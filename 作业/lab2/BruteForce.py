import time
from FileOption import  FileOption

def PowerSetsBinary(items):
    N = items.__len__()
    retSubset=[]
    for i in range(2**N):
        combo = frozenset([])
        for j in range(N):
            if(i >> j ) % 2 == 1:
                combo = combo.union(items[j])
                # print("i=",i,"j=",j)
        if combo.__len__()!= 0:
            retSubset.append(combo)
    return retSubset

def getBrute(datatype=0,minSup=0.5,minConf=0.7,getFreqitems=True,getRules=False):
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

    minSup = minSup * transactions.__len__()
    minConf = minConf

    print("Brute Force 开始")

    subSets = PowerSetsBinary(items)  # 得到items的所有子集
    # print(subSets)
    print("一共有",subSets.__len__(),"个子集")
    supDict = {}
    index = 1
    for subset in subSets:
        if index%10000 == 0:
            print("处理第",index,"项")
        index += 1
        supCnts = 0
        for trans in transactions:
            if subset.issubset(trans):
                supCnts += 1
        if supCnts >= minSup:
            supDict[subset] = supCnts/transactions.__len__()

    for k,v in supDict.items():
        print(list(k),"->",v)

    print("频繁项集个数", supDict.__len__())



if __name__ == '__main__':

    start = time.time()  # 计算程序运行时间

    fop = FileOption()
    # items, transactions = fop.get_data('dataset/Groceries_test.csv')
    items, transactions = fop.get_data('dataset/bftest.csv')
    # items, transactions = fop.get_data('dataset/bftest.csv')

    minSup = 0.05 * transactions.__len__()
    minConf = 0.05

    subSets = PowerSetsBinary(items)  # 得到items的所有子集
    # print(subSets)
    print("一共有",subSets.__len__(),"个子集")
    supDict = {}
    index = 1
    for subset in subSets:
        if index%10000 == 0:
            print("处理第",index,"项")
        index += 1
        supCnts = 0
        for trans in transactions:
            if subset.issubset(trans):
                supCnts += 1
        if supCnts >= minSup:
            supDict[subset] = supCnts/transactions.__len__()

    outcome = []
    for k,v in supDict.items():
        # print(list(k),"->",v)
        outcome.append((list(k),"->",v))
    freInfo = "一共有"+str(outcome.__len__())+"个频繁项"
    print(outcome)
    end = time.time()

    timeinfo = "运行时间：" + str((end - start)/60) + "min"
    print("运行时间：" + str((end - start)/60) + "min")

    f = open("bf_result.txt", 'w')
    f.write(freInfo)
    f.write('\n')
    for res in outcome:
        f.write(str(res))
        f.write('\n')
    f.write(timeinfo)
    f.close()

