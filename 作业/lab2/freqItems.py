import Apriori as ap
import FPGrowth as fp
import BruteForce as bf
import psutil
import os
import time
import sys

if __name__ == '__main__':
    pid = os.getpid()
    p = psutil.Process(pid)
    print('Process info:')
    print('name: ', p.name())
    print('exe:  ', p.exe())
    start = time.time()  # 计算程序运行时间

    methodType = 0  #使用的方法，0为Apriori法，1为FPGrowth法，2为暴力法（暴力法只能使用datatye=3的数据集，不然会炸）
    datatype = 2  # 挖掘的数据集，0为Groceies数据集，1为UNIX数据集, 2为测试暴力算法测试集
    minSup = 0.01  # 最小支持度
    minConf = 0.05  # 最小值置信度
    getFreqitems = True  # 是否输出频繁项集（暴力法只能输出关联规则）
    getRules = True  # 是否输出关联规则

    if methodType == 0:
        ap.getApriori(datatype=datatype,minSup=minSup,minConf=minConf,getFreqitems=getFreqitems,getRules=getRules)
    elif methodType == 1:
        fp.getFPGrowth(datatype=datatype,minSup=minSup,minConf=minConf,getFreqitems=getFreqitems,getRules=getRules)
    elif methodType == 2:
        if datatype != 2:
            print("暴力方法只能处理小规模数据")
            sys.exit(-1)
        bf.getBrute(datatype=datatype,minSup=minSup,minConf=minConf,getFreqitems=getFreqitems,getRules=getRules)
    else:
        print("请选择正确的方法类型")
        sys.exit(-1)

    end = time.time()
    info = p.memory_full_info()
    memory = info.uss / 1024. / 1024.
    print('Memory used: {:.2f} MB'.format(memory))

    print("运行时间：" + str(end - start) + "s")

