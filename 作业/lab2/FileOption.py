import pandas as pd
import numpy as np
import time


class FileOption:
    '''
    用于读取和清洗数据集
    '''
    dataset_original = []  # 初始读入的数据
    items = []  # 数据集中项的种类
    transactions = []   # 数据集

    def clear_class(self):
        self.dataset_original = []  # 初始读入的数据
        self.items = []  # 数据集中项的种类
        self.transactions = []  # 数据集

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

    def get_UNIX_data(self):
        """
        默认数据集放在 UNIX_usage/下
        """
        path0 = 'dataset/UNIX_usage/USER'
        path1 = '/sanitized_all.981115184025'
        out = []
        for i in range(9):
            filename = path0+str(i)+path1
            f = open(filename, 'r')
            lines = f.readlines()
            startFlag = "**SOF**"
            endFalg = "**EOF**"
            transaction = []
            for l in lines:  # 每次取出一行
                t = l.strip('\n')  # 去掉行尾的换行符
                if t == startFlag:
                    continue
                elif t == endFalg:
                    self.transactions.append(transaction)
                    for item in transaction:
                        if not [item] in out:
                            out.append([item])
                    transaction = []
                else:
                    transaction.append(t)

        out.sort()
        self.transactions = list(map(set, self.transactions))
        # 使用frozenset是为了后面可以将这些值作为字典的键
        self.items = list(map(frozenset, out))  # frozenset一种不可变的集合，set可变集合
        return self.items, self.transactions

    def get_data(self,filename):
        self.get_frozenset(filename=filename)
        return self.items, self.transactions

    def get_data_FP(self,filename):
        self.get_frozenset(filename=filename)
        retDict = {}
        count = 0
        for trans in self.transactions:
            if frozenset(trans) in retDict:
                retDict[frozenset(trans)] = retDict[frozenset(trans)]+1
                count = count + 1
                # print("++")
            else:
                retDict[frozenset(trans)] = 1
        print("重复个数："+str(count))
        return retDict