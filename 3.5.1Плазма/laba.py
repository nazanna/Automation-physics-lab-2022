# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 12:24:24 2022

@author: anna
"""

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


def make_all():

    plt.figure(dpi=500, figsize=(8, 5))
    vac_discharge()
    plt.savefig('U(I)_discharge')
    plt.show()

    plt.figure(dpi=500, figsize=(8, 5))
    vac_probe()


def vac_discharge():
    data = make_dic('V(I)_discharge.csv')
    data['I_1'] *= 6/150
    data['U_1'] *= 10
    x = []
    y = []
    for i in range(len(data['U_1'])):
        if data['I_1'][i] <= 1.8:
            y.append(data['U_1'][i])
            x.append(data['I_1'][i])
    x = np.array(x)
    y = np.array(y)

    k, b, sigma = make_graffic(y=y, x=x, xlabel='I, mA',
                               ylabel='U, V', caption_point='', xerr=0.003*x,
                               yerr=0.002*y)

    make_point_grafic(y=data['U_1'], x=data['I_1'], ylabel='U, V',
                      xlabel='I, mA', caption='', xerr=0.003*data['I_1'],
                      yerr=0.002*data['U_1'])

    print('R_dif=', k*10**3, '+-', sigma[0]*10**3)


def vac_probe():
    big_data = {'I_en': [], 'I_en_sigma': [], 'I_in': [], 'k': [],
                'I_in_sigma': [], 'k_sigma': []}
    I_p = [1.5, 3, 3.4]
    for i in I_p:
        name = 'Probe_'+str(i)+'.csv'
        num = int(i+0.6)-2
        data = make_dic(name)
        cap = '$I_p$  = ' + str(i)+' mA'
        x = data['U']
        y = data['I']
        xlabel = 'U, V'
        ylabel = 'I, $\mu$A'
        color = colors[num]
        x_lin_big = []
        x_lin_sm = []
        y_lin_big = []
        y_lin_sm = []
        x_lin_ave = []
        y_lin_ave = []
        for j in range(len(data['U'])):
            if data['U'][j] >= 12.5:
                x_lin_big.append(data['U'][j])
                y_lin_big.append(data['I'][j])
            elif data['U'][j] <= -12.5:
                x_lin_sm.append(data['U'][j])
                y_lin_sm.append(data['I'][j])
            elif data['U'][j] <= 6 and data['U'][j] >= -6:
                x_lin_ave.append(data['U'][j])
                y_lin_ave.append(data['I'][j])

        xerr = 0.003
        yerr = 0.002
        k, b, sigma = make_graffic(x_lin_big, y_lin_big, xlabel=xlabel,
                                   ylabel=ylabel, caption_point='', xerr=0,
                                   yerr=0, color=color)
        big_data['I_en'].append(b*10**(-6)*3*10**9)
        big_data['I_en_sigma'].append(sigma[1]*10**(-6)*3*10**9)
        make_line_grafic(0, xmax=max(x_lin_big), xerr=0, yerr=0, xlabel=xlabel,
                         ylabel=ylabel, k=k, b=b, caption='', linestyle=':',
                         color=color[1])
        plt.scatter(0, b, color=color[1], marker=0, s=15, linewidths=5)
        k, b, sigma = make_graffic(x_lin_sm, y_lin_sm, xlabel=xlabel,
                                   ylabel=ylabel, caption_point='', xerr=0,
                                   yerr=0, color=color, koef=[1.1, 0.9])
        big_data['I_in'].append(-b*10**(-6)*3*10**9)
        big_data['I_in_sigma'].append(sigma[1]*10**(-6)*3*10**9)
        make_line_grafic(xmax=0, xmin=min(x_lin_sm), xerr=0, yerr=0,
                         xlabel=xlabel, ylabel=ylabel, k=k, b=b, caption='',
                         linestyle=':', color=color[1])
        make_point_grafic(x, y, xlabel, ylabel, caption=cap, xerr=xerr*x,
                          yerr=yerr*y, center=True, color=color[0])
        plt.scatter(0, b, color=color[1], marker=0, s=15, linewidths=5)
        k, b, sigma = approx(x_lin_ave, y_lin_ave, b=2, sigma_y=[0])
        big_data['k'].append(k*10**(-6)*3*10**9*3*10**2)
        big_data['k_sigma'].append(sigma[0]*10**(-6)*3*10**9*3*10**2)

    plt.legend()
    plt.savefig('I(U)_probe')
    plt.show()
    for i in big_data.keys():
        big_data[i] = np.array(big_data[i])
    k_b = 1.38*10**(-16)
    e = 4.8 * 10**(-10)
    T_e = 1/2*big_data['I_in']/big_data['k']*e/k_b  # ЭВ
    T_e_sigma = T_e*((big_data['I_in_sigma']/big_data['I_in'])**2+
                     (big_data['k_sigma']/big_data['k'])**2)**0.5
    print('T_e = ', *T_e, 'К')
    print('T_e_sigma = ', *T_e_sigma, 'К')
    print('T_e = ', *T_e/11606, 'эВ')
    print('T_e_sigma = ', *T_e_sigma/11606, 'эВ')
    S = np.pi * 0.2 * 5.2 * 10 ** (-2)
    m_i = 22 * 1.66 * 10 ** (-24)
    m_e = 9.1 * 10 ** (-28)
    n_i = 2.5*big_data['I_in']/e/S*(m_i/2/T_e/k_b)**0.5
    n_i_sigma = n_i*((big_data['I_in_sigma']/big_data['I_in'])**2+
                     1/4*(T_e_sigma/T_e)**2)**0.5
    print('n_i = ', *n_i/10**(10), '10^10')
    print('n_i_sigma = ', *n_i_sigma/10**(10), '10^10')
    w_p = (4*np.pi*n_i*e**2/m_e)**0.5
    w_p_sigma = w_p * n_i_sigma/n_i/2
    print('w_p =', *w_p/10**9, '10^9 рад/с')
    print('w_p_sigma =', *w_p_sigma/10**9, '10^9 рад/с')
    r_De = (k_b*T_e/4/np.pi/n_i/e**2)**0.5
    r_De_sigma = r_De * ((T_e_sigma/T_e)**2 + (n_i_sigma/n_i)**2)**0.5
    print('r_De =', *r_De*10**3, '10^-3 см')
    print('r_De_sigma =', *r_De_sigma*10**3, '10^-3 см')
    T_i = 300
    r_D = (k_b*T_i/4/np.pi/n_i/e**2)**0.5
    r_D_sigma =  r_D * n_i_sigma/n_i
    print('r_D =', *r_D*10**3, '10^-3 см')
    print('r_D_sigma =', *r_D_sigma*10**3, '10^-3 см')
    N_D = 4/3*np.pi*n_i*r_D**3
    N_D_sigma = N_D * (9*(r_D_sigma/r_D)**2 + (n_i_sigma/n_i)**2)**0.5
    print('N_D = ', *N_D)
    print('N_D_sigma = ', *N_D_sigma)
    alpha = n_i * k_b * T_e / (2*133*10)
    alpha_sigma = alpha * ((T_e_sigma/T_e)**2 + (n_i_sigma/n_i)**2)**0.5
    print('alpha = ', *alpha*10**5, '10^-5')
    print('alpha_sigma = ', *alpha_sigma*10**5, '10^-5')
    
    
    plt.figure(dpi=500, figsize=(8, 5))
    ax = plt.gca()
    ax.set_xlabel("radius [m]", fontsize=16)
    ax.set_ylabel(r"surface area ($m^2$)", fontsize=16, color="blue")
    for label in ax.get_yticklabels():
        label.set_color("blue")
    
    I_p = np.array(I_p)
    make_point_grafic(I_p, T_e/10**4, ylabel='$T_e, 10^4 \cdot K$',
                      xlabel='$I_p$, mA', caption='', xerr=I_p*xerr, 
                      yerr=T_e_sigma/10**4, color='blue', s=60)
    ax2 = ax.twinx()
    ax2.set_ylabel(r"volume ($m^3$)", fontsize=16, color="red")
    for label in ax2.get_yticklabels():
        label.set_color("red")

    make_point_grafic(I_p, n_i/10**10, ylabel='$n_e, 10^{10} \cdot см^{-3}$',
                      xlabel='$I_p$, mA', caption='', xerr=I_p*xerr, 
                      yerr=n_i_sigma/10**10, color='red', s=30)

    plt.savefig('T,n(I_p)')
    plt.show()


colors = [['green', 'mediumpurple'], ['orange', 'sandybrown'],
          ['maroon', 'rosybrown'], ['darkblue', 'gold'],
          ['crimson', 'greenyellow'], ['indigo', 'lightgreen']]
make_all()
