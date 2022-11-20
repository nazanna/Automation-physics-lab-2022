#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 19:49:57 2022

@author: anna
"""
import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


class Data:
    def __init__(self, x=[], y=[], xlabel='', ylabel='', caption='', xerr=[],
                 yerr=[], through_0=0, data_filename='', color=None,
                 centering=None, size=15, coefficient=[0.9, 1.1], saving=None):
        self.x = x
        self.y = y
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.caption = caption
        self.cap_point = None
        self.line_point = None
        self.xerr = xerr
        self.yerr = yerr
        self.make_errors(xerr, yerr)
        self.through_0 = through_0
        if not color:
            self.color = ['limegreen', 'indigo']
        else:
            self.color = color
        self.centering = centering
        self.size = size
        self.coefficient = coefficient
        self.data_filename = data_filename
        self.saving = saving

    def make_errors(self, xerr=[], yerr=[]):
        if not len(xerr):
            xerr = self.xerr
        if not len(yerr):
            yerr = self.yerr
        if not len(xerr):
            xerr = 0
        if not len(yerr):
            yerr = 0
        if type(yerr) == float or type(yerr) == int:
            self.yerr = [yerr for _ in self.y]
        else:
            self.yerr = yerr
        if type(xerr) == float or type(xerr) == int:
            self.xerr = [xerr for _ in self.x]
        else:
            self.xerr = xerr

    def read_csv(self):
        with open(self.data_filename) as file:
            reader = list(csv.reader(file))
        data = np.array(reader)
        dic = []
        for i in range(len(data[0])):
            micro_data = []
            for j in range(len(data)):
                micro_data.append(data[j][i])
            dic.append(micro_data)
        data = dic
        dic = {}
        for i in range(len(data)):
            dic[data[i][0]] = np.array(data[i][1:]).astype(np.float)
        data = dic
        self.data = data

    def make_point_grafic(self):
        self.make_errors()
        if self.cap_point:
            cap = self.cap_point
        else:
            cap = self.caption
        if self.xerr[1] != 0 or self.yerr[1] != 0:
            plt.errorbar(self.x, self.y, yerr=self.yerr, xerr=self.xerr, linewidth=4,
                         linestyle='', label=cap, color=self.color[0],
                         ecolor=self.color[0], elinewidth=1, capsize=3.4,
                         capthick=1.4)
        else:
            plt.scatter(self.x, self.y, linewidth=0.005, label=cap,
                        color=self.color[0], edgecolor='black', s=self.size)

        if not self.centering:
            plt.xlabel(self.xlabel)
            plt.ylabel(self.ylabel)
        else:
            self.ax = plt.gca()
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
            self.ax.spines['bottom'].set_position('zero')
            self.ax.spines['left'].set_position('zero')
            self.ax.set_xlabel(self.ylabel, labelpad=-180, fontsize=14)
            self.ax.set_ylabel(self.xlabel, labelpad=-260,
                               rotation=0, fontsize=14)

    def make_line_grafic(self, k, b):
        if min(self.x) > 0:
            xmin = min(self.x)*self.coefficient[0]
        else:
            xmin = min(self.x)*self.coefficient[1]

        if max(self.x) > 0:
            xmax = max(self.x)*self.coefficient[1]
        else:
            xmax = max(self.x)*self.coefficient[0]

        if self.line_point:
            cap = self.line_point
        else:
            cap = self.caption
        x = np.arange(xmin, xmax, (xmax-xmin)/10000)
        plt.plot(x, k*x+b, label=cap, linewidth=2.4,
                 linestyle='-', color=self.color[1])

    def make_grafic(self, named_by_points=True):
        plt.figure(dpi=500, figsize=(8, 5))
        self.make_errors()
        if named_by_points:
            self.cap_point = self.caption
            self.line_point = None
        else:
            self.line_point = self.caption
            self.cap_point = None
        self.make_point_grafic()

        k, b, sigma = self.approx()
        sigma[0] = abs(k*((sigma[0]/k)**2+(np.mean(self.yerr)/np.mean(self.y))**2 +
                          (np.mean(self.xerr)/np.mean(self.x))**2)**0.5)
        if (b != 0):
            sigma[1] = abs(b*((sigma[1]/b)**2+(np.mean(self.yerr)/np.mean(self.y))**2 +
                              (np.mean(self.xerr)/np.mean(self.x))**2)**0.5)
        else:
            sigma[1] = 0

        self.make_line_grafic(k, b)
        plt.legend()
        if self.saving:
            plt.savefig(self.saving)
        return k, b, sigma

    def approx(self):
        if self.yerr[0] != 0:
            sigma_y = [1/i**2 for i in self.y]
        else:
            sigma_y = np.array([1 for _ in self.y])
        if self.through_0 == 0:
            def f(x, k):
                return k*x
            k, sigma = curve_fit(f, xdata=self.x, ydata=self.y, sigma=sigma_y)
            sigma = np.sqrt(np.diag(sigma))
            return k[0], 0, [sigma[0], 0]
        else:
            def f(x, k, b):
                return x*k + b
            k, sigma = curve_fit(f, xdata=self.x, ydata=self.y, sigma=sigma_y)
            sigma_b = np.sqrt(sigma[1][1])
            b = k[1]
            k = k[0]
            sigma = np.sqrt(sigma[0][0])
            return k, b, [sigma, sigma_b]
