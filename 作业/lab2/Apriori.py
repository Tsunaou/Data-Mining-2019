import pandas as pd
import numpy as np

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



if __name__ == '__main__':
    fop = FileOption()
    items, transactions = fop.get_data('dataset/Groceries.csv')
    print(items)
