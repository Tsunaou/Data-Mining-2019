import Apriori
import time
from FileOption import  FileOption



# 树节点用类来封装所有属性（以便解决复杂的数据存储问题）
class treeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue  # 元素名
        self.count = numOccur  # 该路径下该元素次数
        self.nodeLink = None  # 用来指向它的相同元素位置不同的节点的位置
        self.parent = parentNode  # 获取父节点，该功能方便后面查找前缀路径（条件模式基）
        self.children = {}  # 该节点的子节点

    def inc(self, numOccur):
        self.count += numOccur

    # 画树便于直观的观察和调试（实际代码意义不大，但很重要）
    def disp(self, ind=1):
        print('  ' * ind, self.name, ' ', self.count)
        for child in self.children.values():
            child.disp(ind + 1)


# 创建树的主要封装函数
def createTree(dataSet, minSup=1):  # 从数据集创建FP-tree但不挖掘
    headerTable = {}
    # 遍历两次数据集
    # 第一次遍历数据集 计算所有元素的频率，返回字典样式
    for trans in dataSet:
        for item in trans:
            if item in headerTable:
                headerTable[item] = headerTable[item] + dataSet[trans]
            else:
                headerTable[item] = dataSet[trans]

    # 此时headerTable中记录的是每个item的频数num，此时若num < minSup，则必然不是频繁项集的元素
    for k in list(headerTable.keys()):  # 循环所有的键，去除小于阈值的键值对
        if headerTable[k] < minSup:  # py3字典在遍历的时候不能更改，所以需要list(a.keys())
            del (headerTable[k])

    freqItemSet = set(list(headerTable.keys()))
    if freqItemSet.__len__() == 0:
        return None, None  # 如果没有满足最小minSup的元素则退出

    for k in headerTable:  # 后面试试在前面的for中就构建好！！！
        headerTable[k] = [headerTable[k], None]  # 重新构造 headerTable （计数值，指向第一个元素项的指针）

    retTree = treeNode('Null Set', 1, None)  # 构建最初的空值树

    # 第二次遍历数据集 构建FP树（只考虑第一次判定的频繁项
    for tranSet, count in dataSet.items():
        localD = {}
        for item in tranSet:  # 为每条筛选后不为0的记录排序
            if item in freqItemSet:  # 如果所有频繁项中有该值
                localD[item] = headerTable[item][0]
        if localD.__len__() > 0:
            # print(localD) #{'z': 5, 'r': 3}
            # 排序主要步骤：通过sorted方法排序，排序的值key=items获得字典的值的第二个值（即元素个数），reverse=True表示降序排序，最后通过列表中只保存元素，不保留个数
            orderedItems = [v[0] for v in sorted(localD.items(), key=lambda p: p[1], reverse=True)]  # ['z','r']
            updateTree(orderedItems, retTree, headerTable, count)  # 使用有序的频繁项集填充树
    return retTree, headerTable  # 返回树和头表


# 将每条有序项集添加到树中
def updateTree(items, inTree, headerTable, count):
    if items[0] in inTree.children:  # 递归时都先判断当前画树的值是否在树的子节点上，如果在则不需要画，只需增加count值
        inTree.children[items[0]].inc(count)  # 给该子节点增加count值（通过类的函数inc）
    else:
        # 如果不在则需要画新的树节点 并且(由于新画了节点，所以需要将相同的该元素节点指向它，若是第一次则用头表指向它)
        inTree.children[items[0]] = treeNode(items[0], count, inTree)  # 画树只需要调用类的子函数treeNode即可
        # 更新头表
        if headerTable[items[0]][1] == None:  # 若头表中该值没有连接过则
            headerTable[items[0]][1] = inTree.children[items[0]]  # 创建link连接，将头表该元素字典的列表的第二个元素记录为该树节点
        else:  # 若有link连接则更新
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])  # 传入（原来头表指向的节点，新画的节点）
    if len(items) > 1:  # 当还有元素时，则继续调用updateTree更新FP树
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)


# 更新头表
def updateHeader(nodeToTest, targetNode):  # 这个版本不使用递归
    while (nodeToTest.nodeLink != None):  # 不要使用递归来遍历链表！！
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode


# 获取一条前缀路径
def ascendTree(leafNode, prefixPath):  # 从末节点回溯到根节点
    if leafNode.parent != None:  # 由于前面画节点的时候，保存了上一个节点为下一个节点的父节点
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)  # 回溯到根节点

# 获取条件模式基（前缀路径集合）
def findPrefixPath(basePat, treeNode):  # treeNode comes from header table
    condPats = {}
    while treeNode != None:
        prefixPath = []
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1:
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        treeNode = treeNode.nodeLink  # 获取下一个前缀路径的最后一个节点
    return condPats  # {每条前缀路径：最后一个元素的计数值}


# 创建条件树  第一个参数意义不大     最小阈值  {}集合      []列表
def mineTree(inTree, headerTable, minSup, preFix, freqItemList,L_sum,supDict):
    # 错误代码说明：p是：('r', [3, <__main__.treeNode object at 0x000002251A5F4BA8>])  p[1]是：[3, <__main__.treeNode object at 0x000002251A5F4BA8>]
    # 所以还需要对p[1]取[0]，得到key=3，用计数值排序而不是树结构排序
    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p: p[1][0])]  # 头表排序，只取键'r'
    print("------------------------------------")
    print("bigL:",bigL)
    L_sum[0] = L_sum[0] + bigL.__len__()
    print("L_sum=",bigL.__len__())
    print("bigL.len:",bigL.__len__())
    for basePat in bigL:  # 从头表的底部开始 ['r', 's', 't', 'y', 'x', 'z']
        newFreqSet = preFix.copy()
        print("oldPreqSet",newFreqSet)
        newFreqSet.add(basePat)  # 添加频繁元素到上一次的集合中
        print("newPreqSet",newFreqSet)
        freqItemList.append(newFreqSet)  # 这个列表用来保存所有的频繁项集

        condPattBases = findPrefixPath(basePat, headerTable[basePat][1])  # 找到条件模式基（即前缀路径集合）
        print("前缀路径(条件模式基)：",condPattBases)
        # 计算单项个数
        if(newFreqSet.__len__() == 1):
            condSum = headerTable[basePat][0]
            # for k,v in condPattBases.items():
            #     condSum += v
            if frozenset(newFreqSet) in supDict:
                supDict[frozenset(newFreqSet)] = supDict[frozenset(newFreqSet)] + condSum
            else:
                supDict[frozenset(newFreqSet)] = condSum
        # 用该元素的条件模式基来创建该元素条件FP树
        myCondTree, myHead = createTree(condPattBases, minSup)  # 返回 条件FP树、头表
        f1 = False
        f2 = False
        if myCondTree != None:
            f1 = True
            myCondTree.disp()
        # print(myHead)
        if myHead != None:  # 继续挖掘FP树
            f2 = True
            print("myHead != None",myHead)
            mineTree(myCondTree, myHead, minSup, newFreqSet, freqItemList,L_sum,supDict)
        else:
            print("myHead == None")
        if(f1^f2):
            print("f1 xor f2:",f1^f2 )
            assert (0)
        print("-------")






if __name__ == '__main__':

    start = time.time()  # 计算程序运行时间

    fop = FileOption()
    fop.clear_class()
    initSet = fop.get_data_FP('dataset/Groceries.csv')
    # initSet = fop.get_data_FP('dataset/testfp.csv')
    lencnt = 0
    for k,v in initSet.items():
        lencnt += v
    minSup = lencnt * 0.05
    myFPtree, myHeaderTable = createTree(initSet, minSup)  # FP树 头表

    myFPtree.disp()


    # 创建条件FP树，并获得频繁项集
    freqItems = []
    L_sum = []
    L_sum.append(0)
    supDict = {}
    mineTree(myFPtree, myHeaderTable, minSup, set([]), freqItems,L_sum,supDict)
    print(freqItems)
    end = time.time()
    print("频繁项集个数为："+str(freqItems.__len__()))
    for k,v in supDict.items():
        print(k,"->",v/lencnt)
    print("运行时间：" + str(end - start) + "s")

