# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy.optimize import curve_fit


def read_csv(file_name):
    with open(file_name) as file:
        reader = list(csv.reader(file, delimiter=';',
                      quotechar=',', quoting=csv.QUOTE_MINIMAL))
    return reader


def make_latex_table(data):
    table = []
    table.append("\\begin{table}".replace('//', '\\'))
    table.append("\label{}".replace('/', '\\'))
    table.append('\caption{}'.replace('/', '\\'))
    leng = len(data[0])
    stroka = 'c'.join(['|' for _ in range(leng+1)])
    table.append('\\begin{tabular}{'.replace('//', '\\')+stroka+'}')
    table.append('\hline')
    for i in range(len(data)):
        table.append(' & '.join(data[i]) + ' \\\\')
        table.append('\hline')
    table.append("\end{tabular}".replace('/', '\\'))
    table.append("\end{table}".replace('/', '\\'))
    return table


def make_point_grafic(x, y, xlabel, ylabel, caption, xerr, yerr,
                      subplot=None, color=None, center=None, s=15):
    if not subplot:
        subplot = plt
    if type(yerr) == float or type(yerr) == int:
        yerr = [yerr for _ in y]
    if type(xerr) == float or type(xerr) == int:
        xerr = [xerr for _ in x]

    if xerr[1] != 0 or yerr[1] != 0:
        subplot.errorbar(x, y, yerr=yerr, xerr=xerr, linewidth=4,
                         linestyle='', label=caption, color=color,
                         ecolor=color, elinewidth=1, capsize=3.4,
                         capthick=1.4)
    else:
        subplot.scatter(x, y, linewidth=0.005, label=caption,
                        color=color, edgecolor='black', s=s)
    # ax = plt.subplots()
    # ax.grid())
    if not center:
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
    else:
        ax = plt.gca()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_position('zero')
        ax.spines['left'].set_position('zero')
        ax.set_xlabel(ylabel, labelpad=-180, fontsize=14)    # +
        ax.set_ylabel(xlabel, labelpad=-260, rotation=0, fontsize=14)


def make_line_grafic(xmin, xmax, xerr, yerr, xlabel, ylabel, k, b, caption,
                     subplot=None, color=None, linestyle='-'):
    if not subplot:
        subplot = plt
    x = np.arange(xmin, xmax, (xmax-xmin)/10000)
    subplot.plot(x, k*x+b, label=caption, color=color, linewidth=1.4,
                 linestyle=linestyle)


def make_graffic(x, y, xlabel, ylabel, caption_point, xerr, yerr, k=None,
                 b=None, filename=None, color=None, koef=[0.9, 1.1], s=None):
    if not color:
        color = ['limegreen', 'indigo']
    if not s:
        make_point_grafic(x, y, xlabel=xlabel,
                      ylabel=ylabel, caption=caption_point,
                      xerr=xerr, yerr=yerr, subplot=plt, color=color[0])
    else:
         make_point_grafic(x, y, xlabel=xlabel,
                      ylabel=ylabel, caption=caption_point,
                      xerr=xerr, yerr=yerr, subplot=plt, color=color[0], s=s)
    if k and b:
        make_line_grafic(xmin=min(x)-1, xmax=max(x)+1, xerr=xerr, yerr=yerr,
                         xlabel='', ylabel='', k=k, b=b,
                         caption='Theoretical dependence', subplot=plt,
                         color='red')
    if type(yerr) == float or type(yerr) == int:
        yerr = [yerr for _ in y]
    k, b, sigma = approx(x, y, b, yerr)
    sigma[0] = abs(k*((sigma[0]/k)**2+(np.mean(yerr)/np.mean(y))**2 +
                      (np.mean(xerr)/np.mean(x))**2)**0.5)
    if (b != 0):
        sigma[1] = abs(b*((sigma[1]/b)**2+(np.mean(yerr)/np.mean(y))**2 +
                          (np.mean(xerr)/np.mean(x))**2)**0.5)
    else:
        sigma[1] = 0

    make_line_grafic(xmin=min(x)*koef[0], xmax=max(x)*koef[1], xerr=xerr,
                     yerr=yerr, xlabel='', ylabel='', k=k, b=b, caption=None,
                     subplot=plt, color=color[1])
    plt.legend()
    return k, b, sigma


def approx(x, y, b, sigma_y, f=None):
    if sigma_y[0] != 0:
        sigma_y = [1/i**2 for i in sigma_y]
    else:
        sigma_y = np.array([1 for _ in y])
    if f is None:
        if b == 0:
            def f(x, k):
                return k*x
            k, sigma = curve_fit(f, xdata=x, ydata=y, sigma=sigma_y)
            sigma = np.sqrt(np.diag(sigma))
            return k, b, [sigma, 0]
        else:
            def f(x, k, b):
                return x*k + b
            k, sigma = curve_fit(f, xdata=x, ydata=y, sigma=sigma_y)
            sigma_b = np.sqrt(sigma[1][1])
            b = k[1]
            k = k[0]
            sigma = np.sqrt(sigma[0][0])

            return k, b, [sigma, sigma_b]
    else:
        k, sigma = curve_fit(f, xdata=x, ydata=y, sigma=sigma_y)
        sigma = np.sqrt(np.diag(sigma))
        b = k[1]
        k = k[0]
        return k, b, sigma


def find_delivation(data):
    data = np.array(data).astype(np.float)
    s = sum(data)/len(data)
    su = 0
    for i in data:
        su += (i-s)**2
    return (su/(len(data)-1))**0.5


def make_dic(filename):
    data = np.array(read_csv(filename))
    data = np.transpose(data)
    dic = {}
    for i in range(len(data)):
        dic[data[i][0]] = np.array(data[i][1:]).astype(np.float)
    data = dic
    return data


def make_fun(A0, T):
    def f(t, k, b):
        return A0/(1+A0*b*t)-k*0*A0*t/T
    return f


def make_fun_grafic(xmin, xmax, xerr, yerr, xlabel, ylabel, f, k, b, caption,
                    subplot=None, color=None):
    if not subplot:
        subplot = plt
    x = np.arange(xmin, xmax, (xmax-xmin)/10000)
    subplot.plot(x, f(x, k, b), label=caption, color=color)
    
    
    
    
def make_all():
    part_1_1()
    part_1_2()
    part_2()
    part_3()
    
    
def part_1_1():
    plt.figure(dpi=500, figsize=(8, 5))
    data = make_dic("dnu(tau).csv")
    x = 1 / data["tau"]*100
    y = data['d_nu']/10**4
    xlabel = "1/"+greek_letters[48]+'$,10^4$Гц'
    ylabel = greek_letters[0]+greek_letters[41]+'$,10^4$ Гц'
    k, b, sigma = make_graffic(x, y, xlabel, ylabel,
                 caption_point='', xerr=0, yerr=0, s=40)
    print(k, sigma[0])
    plt.savefig("dnu(tau)")
    plt.show()


def part_1_2():
    fig, ax = plt.subplots(figsize=(10, 6))
    data = make_dic("a(n).csv")
    v = 1000
    t = 50 * 10 **- 6
    T = 1 / v
    N = 200
    V0 = 300
    vu = [n/T for n in range(2, N)]
    c = [abs(V0*t/T*np.sin(n*t*np.pi/T)/(n*t*np.pi/T)) for n in range(2, N)]
    for i in range(len(vu)):
        plt.scatter(vu[i], c[i], linewidth=0.005, label='',
                        color='purple', s=15)
        ax.vlines(vu[i], 0, c[i], colors='purple')
    ax.set_xlabel(greek_letters[41]+', Hz')
    ax.set_ylabel("$a_n$, мВ")
    plt.savefig("a(n)")
    plt.show()
    
def part_2():
    plt.figure(dpi=500, figsize=(8, 5))
    data = make_dic("T(dnu).csv")
    x = 1 / data["T"]*10**3
    y = data['dnu']
    xlabel = "1/"+greek_letters[48]+'$, $Гц'
    ylabel = greek_letters[0]+greek_letters[41]+'$,10^4$ Гц'
    k, b, sigma = make_graffic(x, y, xlabel, ylabel,
                 caption_point='', xerr=0, yerr=0, s=40)
    print(k, sigma[0], -sigma[0]/k*100)
    plt.savefig("T(dnu)")
    plt.show()
    
def part_3():
    plt.figure(dpi=500, figsize=(8, 5))
    data = make_dic("a(m).csv")
    otn = data['a_b']/data['a_c']
    k, b, sigma = make_graffic(data['m']/100, otn, 'm', '$а_{бок}/a_{осн}$', 
                               caption_point='', xerr=0, yerr=0, s=40)
    print(k, sigma[0])
    plt.savefig("a(m)")
    plt.show()
    
    
    
    
    
greek_letters=[chr(code) for code in range(916,980)]
print(greek_letters)

make_all()   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
