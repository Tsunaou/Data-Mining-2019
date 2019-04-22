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
        if combo.__len__()!= 0:
            retSubset.append(combo)
    return retSubset

if __name__ == '__main__':

    start = time.time()  # 计算程序运行时间

    fop = FileOption()
    # items, transactions = fop.get_data('dataset/Groceries_test.csv')
    items, transactions = fop.get_data('dataset/testfp.csv')
    # items, transactions = fop.get_data('dataset/test.csv')

    minSup = 0.05 * transactions.__len__()
    minConf = 0.05

    subSets = PowerSetsBinary(items)  # 得到items的所有子集
    # print(subSets)
    print("一共有",subSets.__len__(),"个子集")
    supDict = {}
    index = 1
    for subset in subSets:
        # print("处理第",index,"项")
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

