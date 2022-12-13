# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 19:17:27 2022

@author: anna
"""


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
    subplot.plot(x, k*x+b, label=caption, color=color, linewidth=2.4,
                 linestyle=linestyle)


def make_graffic(x, y, xlabel, ylabel, caption_point, xerr, yerr, k=None,
                 b=None, filename=None, color=None, koef=[0.9, 1.1], cap=1):
    if not color:
        color = ['limegreen', 'indigo']
    if cap == 1:
        cap_point = caption_point
        line_point = None
    else:
        line_point = caption_point
        cap_point = None
    make_point_grafic(x, y, xlabel=xlabel,
                      ylabel=ylabel, caption=cap_point,
                      xerr=xerr, yerr=yerr, subplot=plt, color=color[0])
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
                     yerr=yerr, xlabel='', ylabel='', k=k, b=b,
                     caption=line_point, subplot=plt, color=color[1])
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
            return k[0], b, [sigma[0], 0]
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


def B(x, b, c, d):
    return x**2*b+x*c+d


def make_grad():
    data = make_dic('grad.csv')
    f_0 = 0.1
    f = data['F']-f_0
    s = 75 * 10 ** -4
    b = f * 10**-3 / s
    x = data['I']
    y = b
    xlabel = '$I_M$, А'
    ylabel = '$B$, Тл'
    caption = ''
    xerr = 1/100*x
    yerr = 1/100*y
    plt.figure(dpi=500, figsize=(8, 5))
    make_point_grafic(x, y, xlabel, ylabel, caption, xerr, yerr)
    a, sigma = curve_fit(B, x, y)
    sigma = abs(np.sqrt(np.diag(sigma))/a)
    eps = (np.min(sigma)**2+0.01**2)**0.5
    x_range = np.arange(min(x), max(x), step=0.001)
    y_fit = B(x_range, a[0], a[1], a[2])
    plt.plot(x_range, y_fit)
    plt.savefig('градуировка')
    plt.show()
    print('a = ', a)
    return (a, eps)


class Exp:
    def __init__(self, e, b, I):
        self.e = e
        self.b = b
        self.I = I


def make_exp(a, eps_b):
    plt.figure(dpi=500, figsize=(10, 6))
    data = make_dic('exp.csv')
    eds = chr(949)
    h=1*10**-3
    e = (data['U_34']-data['U_0'])/10**3
    b = np.array(B(data['I'], a[0], a[1], a[2]))
    big_data = []
    e_big = []
    b_big = []
    I_big = []
    # x=[]
    # y=[]
    # for i in range(len(b)):
    #     if True:
    #         x.append(b[i] * data['I_t'][i])
    #         y.append(e[i])
    # x=np.array(x)
    # y=np.array(y)
    # xlabel = 'I$_{обр} \cdot B$, мА$\cdot $ Tл'
    # ylabel = eds+'$_x$, мВ'
    # caption_point = ''
    # xerr = abs(x*(eps_b**2+0.01**2)**0.5)
    # yerr = abs(5*10**-5*y)
    # k, b1, sigma = make_graffic(x, y, xlabel, ylabel, caption_point, xerr, yerr, b=0)
    # print('all ', -k/h, '+-', sigma[0]/h)
    # plt.show()
    # plt.figure(dpi=500, figsize=(8, 5))
    
    I_t = data['I_t'][0]
    for i in range(len(data['I'])):
        if (I_t == data['I_t'][i]):
            e_big.append(e[i])
            b_big.append(b[i])
            I_big.append(data['I_t'][i])
        else:
            exp = Exp(e_big, b_big, I_big)
            big_data.append(exp)
            e_big = []
            b_big = []
            I_big = []
            I_t = data['I_t'][i]
            i -= 1
    colors = [['forestgreen', 'rosybrown'], ['darkgoldenrod', 'mediumpurple'],
              ['maroon', 'sandybrown'], ['darkblue', 'gold'],
              ['crimson', 'greenyellow'], ['indigo', 'lightgreen'], ['yellow', 'purple']]
    count = 0
    data = {'k': [], 'I': [], 'sig_k': []}
    for i in big_data:
        x = np.array(i.b)
        y = np.array(i.e)
        xlabel = 'B, Тл'
        ylabel = '$U_\perp$, мВ'
        caption_point = 'I = ' + str(i.I[0])+' мА'
        xerr = abs(x*eps_b)
        yerr = abs(5*10**-5*y)
        color = ['black', colors[count][1]]
        count += 1
        k, b, sigma = make_graffic(x, y, xlabel, ylabel, caption_point,
                                   xerr, yerr, color=color, cap=2, b=0)
        data['k'].append(k)
        data['I'].append(i.I[0])
        data['sig_k'].append(sigma[0])
        plt.savefig('E(B)')
        
    plt.figure(dpi=500, figsize=(8, 5))
    x = np.array(data['I'])
    y = np.array(data['k'])
    xlabel = 'I, мА'
    ylabel = 'K, мВ/Тл'
    caption_point = ''
    xerr = abs(x*1/100)
    yerr = data['sig_k']
    k, b, sigma = make_graffic(x, y, xlabel, ylabel, caption_point, xerr, yerr, b=0, koef=[1.1, 1.1])
    plt.savefig('K(I)')
    print('R_x ',k*h*10**6, '+-', sigma[0]*10**6*h)
    e_e =1.6*10**-19
    n = 1/(-k*h*e_e)*10**-21
    sigma_n = n*abs(sigma[0]/k)
    print('n = ', n, '+-', sigma_n)
    sig = 1/4.097*5/4/10**-3
    sig_sig = sig*((5*10**-5)**2+(1/100)**2)**0.5
    print('sigma = ', sig, '+-', sig_sig)
    b = -sig*k*h*10**4
    sig_b = b*((sig_sig/sig)**2+(sigma[0]/k)**2)**0.5
    print('b = ', b, '+-', sig_b)

def make_all():
    (a, eps_B) = make_grad()
    make_exp(a, eps_B)


make_all()
