import pandas as pd
import numpy as np
import csv

if __name__ == '__main__':
    filepath = 'Assignment2/dataset/UNIX_usage/USER0/sanitized_all.981115184025'
    savename = 'dataTest.csv'
    f = open(filepath, 'r')
    out = open(savename, 'w')
    lines = f.readlines()
    startFlag = "**SOF**"
    endFalg = "**EOF**"
    newSession = False
    for l in lines:  #每次取出一行
        t = l.strip('\n') # 去掉行尾的换行符
        if t == startFlag:
            newSession = True
            continue
        elif t == endFalg:
            out.write('\n')
        else:
            if newSession:
                newSession = False
            else:
                out.write(',')
            out.write(t)
    out.close()



