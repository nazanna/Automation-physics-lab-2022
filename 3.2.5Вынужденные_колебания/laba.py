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
                 b=None, filename=None, color=None, koef=[0.9, 1.1]):
    if not color:
        color = ['limegreen', 'indigo']
    make_point_grafic(x, y, xlabel=xlabel,
                      ylabel=ylabel, caption=caption_point,
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


def make_smth(r):
    if (r == 0):
        s = 'U(nu)_0.csv'
    else:
        s = 'U(nu)_R.csv'
    nu = chr(957)
    eps_u = 2.5/100
    eps_nu = 0.1/100
    data_0 = make_dic(s)
    nu_m_0 = 0
    U_m_0 = 0
    j = 0
    for i in range(len(data_0['U'])):
        if (data_0['U'][i] >= U_m_0):
            U_m_0 = data_0['U'][i]
            nu_m_0 = data_0['nu'][i]
            j = i
    x = data_0['nu']/nu_m_0
    y = data_0['U']/U_m_0
    eps_nu_0 = abs(data_0['nu'][j-1]-data_0['nu'][j+1])/data_0['nu'][j]
    xerr = eps_nu*2**0.5*x
    yerr = eps_u*2**0.5*y
    xlabel = nu + '/ '+nu+'$_m$'
    ylabel = '$U/U_m$'
    if r == 0:
        caption = 'R = 0'
    else:
        caption = 'R = 100 Ом'
    make_point_grafic(x, y, xlabel, ylabel, caption, xerr, yerr)
    plt.grid(True)
    cons = 0.727
    j1 = len(x)
    j2 = len(x)
    for i in range(len(x)-1):
        if y[i] >= cons and y[i+1] <= cons:
            j2 = i
        if y[i] <= cons and y[i+1] >= cons:
            j1 = i   
    x1 = x[j1] + (cons - y[j1])*(x[j1+1]-x[j1])/(y[j1+1]-y[j1])
    x2 = x[j2] + (cons - y[j2])*(x[j2+1]-x[j2])/(y[j2+1]-y[j2])
    x = np.arange(min(x), max(x), step=0.001)
    y_fit = [cons for _ in x]
    plt.plot(x, y_fit)
    Q = 1/abs(x2-x1)
    err = Q*(eps_nu**2 +eps_nu_0**2+2*eps_u**2)**0.5
    if r == 0: st = 'Q_0 = '
    else: st = 'Q_R = '
    print(st, Q, '+-', err)


def make_ust():
    data = make_dic('ust_0.csv')
    tet = -1/data['n'] * \
        np.log((data['U_0']-data['U_k+n'])/(data['U_0']-data['U_k']))
    Q = np.pi/tet
    eps_u = 2.5/100
    eps_Q = find_delivation(Q)/np.mean(Q)
    sig = np.mean(Q)*(eps_u**2+eps_Q**2)**0.5
    print('Q_0 = ', np.mean(Q),'+-', sig)
    data = make_dic('ust_R.csv')
    tet = -1/data['n'] * \
        np.log((data['U_0']-data['U_k+n'])/(data['U_0']-data['U_k']))
    Q = np.pi/tet
    eps_Q = find_delivation(Q)/np.mean(Q)
    sig = np.mean(Q)*(eps_u**2+eps_Q**2)**0.5
    print('Q_R = ', np.mean(Q),'+-', sig)


def make_all():
    plt.figure(dpi=500, figsize=(8, 5))
    make_smth(0)
    make_smth(1)
    plt.legend()
    plt.savefig('graf')
    make_ust()


make_all()
