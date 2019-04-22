from FileOption import  FileOption
from Apriori import generateRules
from collections import namedtuple
import time


def find_frequent_itemsets(transactions, minSup):

    # 统计数据集中每个项的数目
    items = {}
    for transaction in transactions:
        for item in transaction:
            if item in items:
                items[item] += 1
            else:
                items[item] = 1

    # 将不满足minSup的项去除
    newItems = {}
    for k,v in items.items():
        if v < minSup:
            continue
        newItems[k] = v
    items = newItems

    # 对一条数据进行数据清洗，去除掉非单项频繁项，这样对结果没有影响
    def clean_transaction(transaction):
        transaction = filter(lambda v: v in items, transaction)
        transaction_list = list(transaction)   # 为了防止变量在其他部分调用，这里引入临时变量transaction_list
        transaction_list.sort(key=lambda v: items[v], reverse=True)
        return transaction_list

    master = FPTree()

    # 将清洗后的数据集加入FP Tree
    for trans in transactions:
        trans = clean_transaction(trans)
        master.add(trans)

    # 寻找前缀路径
    def find_with_suffix(tree, suffix):
        for item, nodes in tree.items():
            support = 0
            for n in nodes:
                support += n.count

            if support >= minSup and item not in suffix:
                # New winner!
                found_set = [item] + suffix
                yield (found_set, support)
                # 构造一颗FP条件树
                cond_tree = conditional_tree_from_paths(tree.prefix_paths(item))
                for s in find_with_suffix(cond_tree, found_set):
                    yield s

    for itemset in find_with_suffix(master, []):
        yield itemset

class FPTree(object):
    """
    FP-Growth Tree
    """

    Route = namedtuple('Route', 'head tail')

    def __init__(self):
        # 树的根节点
        self._root = FPNode(self, None, None)
        self._routes = {}  # FP树每个项的HeaderTable

    @property
    def root(self):
        return self._root

    def add(self, transaction):
        point = self._root

        for item in transaction:
            next_point = point.search(item)
            if next_point:
                # 项在FP-Tree中存在，就给该项计数加一
                next_point.increment()
            else:
                # 否则向FP-Tree中增加一个节点，并更新HeaderTable的路径
                next_point = FPNode(self, item)
                point.add(next_point)
                self._update_route(next_point)

            point = next_point

    def _update_route(self, point):
        """
        更新项的HeaderTable路径表
        """
        try:
            route = self._routes[point.item]
            route[1].neighbor = point # route[1] is the tail
            self._routes[point.item] = self.Route(route[0], point)
        except KeyError:
            # 首次建路径表
            self._routes[point.item] = self.Route(point, point)

    def items(self):
        """
        Generate one 2-tuples for each item represented in the tree. The first
        element of the tuple is the item itself, and the second element is a
        generator that will yield the nodes in the tree that belong to the item.
        """
        for item in self._routes.keys():
            yield (item, self.nodes(item))

    def nodes(self, item):
        """
        返回包含目标项的节点序列
        """
        try:
            node = self._routes[item][0]
        except KeyError:
            return

        while node:
            yield node
            node = node.neighbor

    def prefix_paths(self, item):
        """得到目标项的前缀路径"""

        def collect_path(node):
            path = []
            while node and not node.root:
                path.append(node)
                node = node.parent
            path.reverse()
            return path

        return (collect_path(node) for node in self.nodes(item))



def conditional_tree_from_paths(paths):
    """
    根据前缀路径构造条件FP树
    """
    tree = FPTree()
    condition_item = None
    items = set()

    for path in paths:
        if condition_item is None:
            condition_item = path[-1].item

        point = tree.root
        for node in path:
            next_point = point.search(node.item)
            if not next_point:
                items.add(node.item)
                count = node.count if node.item == condition_item else 0
                next_point = FPNode(tree, node.item, count)
                point.add(next_point)
                tree._update_route(next_point)
            point = next_point


    for path in tree.prefix_paths(condition_item):
        count = path[-1].count
        for node in reversed(path[:-1]):
            node._count += count

    return tree

class FPNode(object):
    """
    FP-Tree 的节点
    """

    def __init__(self, tree, item, count=1):
        self._tree = tree       # 树节点
        self._item = item       # 项
        self._count = count     # 该项出现的次数
        self._parent = None     # 父节点
        self._children = {}     # 子节点
        self._neighbor = None   # 用于链接同类项的邻居结点

    def add(self, child):
        """
        为该节点增加一个子节点
        """
        if not child.item in self._children:
            self._children[child.item] = child
            child.parent = self

    def search(self, item):
        """
        查找该节点的子节点中为item的
        """
        if item in self._children:
            return self._children[item]
        else:
            return None

    @property
    def tree(self):
        return self._tree

    @property
    def item(self):
        return self._item

    @property
    def count(self):
        return self._count

    def increment(self):
        self._count += 1

    @property
    def root(self):
        return self._item is None and self._count is None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def neighbor(self):
        return self._neighbor

    @neighbor.setter
    def neighbor(self, value):
        self._neighbor = value




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
        dataset = fop.get_data_FP_new('dataset/bftest.csv')
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


    rules = []
    if getRules:
        rules = generateRules(L, supportData, minConf=minConf)
        for rule in rules:
            print(str(rule[0]) + "->" + str(rule[1]) + ":" + str(rule[2]))

    print("频繁项集个数", result.__len__())
    if getRules:
        print("挖掘到规则数", rules.__len__())


if __name__ == '__main__':

    start = time.time()  # 计算程序运行时间

    fop = FileOption()
    dataset= fop.get_data_FP_new('dataset/Groceries.csv')
    # dataset= fop.get_data_FP_new('dataset/testbf.csv')
    # dataset = fop.get_data_FP_UNIX()
    minSup = dataset.__len__() * 0.02
    minConf = 0.05

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


