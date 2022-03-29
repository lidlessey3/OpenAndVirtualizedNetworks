import matplotlib.pyplot as plt
import numpy as np

def readFile():
    table=[]
    fi = open("lab02/Resources/sales_data.csv", "r")
    headers = fi.readline().strip().split(",")
    for line in fi:
        tmp = line.strip().split(",")
        for i in range(0,9):
            tmp[i] = int(tmp[i])
        table.append({headers[0]:tmp[0], headers[1]:tmp[1],headers[2]:tmp[2], headers[3]:tmp[3], headers[4]:tmp[4], headers[5]:tmp[5], headers[6]:tmp[6], headers[7]:tmp[7], headers[8]:tmp[8]})
    fi.close()
    return table

def ex1():
    table = readFile()
    figure, plot = plt.subplots()
    x = []
    y = []
    for i in range(0,12):
        x.append(table[i]["month_number"])
        y.append(table[i]["total_profit"])
    plot.plot(x, y)
    print(x)
    print(y)
    plt.show()

def ex2():
    table = readFile()
    figure, plot = plt.subplots()
    x = []
    y = []
    for i in range(0,12):
        x.append(table[i]["month_number"])
        y.append(table[i]["total_profit"])
    plot.plot(x, y, label = "Profit data of the year", color = "r", marker = "o", markerfacecolor =  "k", linestyle = " ", linewidth = 3)
    print(x)
    print(y)
    plt.show()

def ex3():
    table=readFile()
    figure, plot = plt.subplots()
    x=[]
    y={}
    y["facecream"] = []
    y["facewash"] = []
    y["toothpaste"] = []
    y["bathingsoap"] = []
    y["shampoo"] = []
    y["moisturizer"] = []
    for i in range(0,12):
        x.append(i+1)
        y["moisturizer"].append(table[i]["moisturizer"])
        y["shampoo"].append(table[i]["shampoo"])
        y["bathingsoap"].append(table[i]["bathingsoap"])
        y["toothpaste"].append(table[i]["toothpaste"])
        y["facewash"].append(table[i]["facewash"])
        y["facecream"].append(table[i]["facecream"])
    plot.plot(x,y["facecream"])
    plot.plot(x,y["facewash"])
    plot.plot(x,y["toothpaste"])
    plot.plot(x,y["bathingsoap"])
    plot.plot(x,y["shampoo"])
    plot.plot(x,y["moisturizer"])
    plt.show()

def ex4():
    table = readFile()
    figure, plot = plt.subplots()
    x = []
    y = []
    for i in range(0,12):
        x.append(table[i]["month_number"])
        y.append(table[i]["toothpaste"])
    plot.scatter(x, y)
    print(x)
    print(y)
    plt.show()

def ex5():
    table = readFile()
    figure, plot = plt.subplots()
    x = []
    y = []
    total = 0
    for i in range(0,12):
        x.append(i+1)
        y.append(table[i]["bathingsoap"])
    plot.pie(y, labels=x, shadow=True, autopct="%1.1f%%")
    plt.savefig("ex5.png")

if __name__ == "__main__":
    ex5()