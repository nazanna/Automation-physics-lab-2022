#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 21:44:23 2022

@author: anna
"""
import os
import csv
import serial
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import time
from PyQt6 import QtCore
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QLabel,
                             QLineEdit,
                             QPushButton,
                             QWidget,
                             QTableWidget,
                             QGridLayout,
                             QTableWidgetItem,
                             QHeaderView,
                             QTextBrowser)
from Analisis_data import Data
from Abstract_window import AbstractWindow


class ChartWindow(AbstractWindow):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle('Обработка данных')
        self.parent = parent

        (a, eps) = self.make_grad()
        print(*a)
        self.make_main(a, eps)
        
        
        self.setWindowTitle('Основной эксперимент. Обработка данных')
        self.resize(1400, 800)

        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)

        pixmap = QPixmap(os.path.join(
            self.parent.folder,
            self.parent.main_chartname))
        self.label = QLabel(self)
        self.label.setScaledContents(True)
        self.label.setFixedSize(0.7*self.width(), 0.9*self.height())
        self.label.setPixmap(pixmap)

        self.text = QTextBrowser()
        text = self.make_text()
        self.parent.text_name = 'Results.txt'
        with open(os.path.join(self.parent.folder, self.parent.text_name), 'w') as file:
            file.write(text)
        self.text.setText(text)
        print(text)

        self.hbox_layout = QGridLayout(self.centralwidget)
        self.hbox_layout.addWidget(self.label, 0, 0)
        self.hbox_layout.addWidget(self.text, 0, 1)

    def B(self, x, b, c, d):
        return 0*x**2*b+x*c+d

    def make_grad(self):
        

        self.parent.flow_dataname = 'Induction_data.csv'
        self.parent.grad_chartname = 'Graduation_chart.png'
        self.parent.data_grad = Data(data_filename=os.path.join(
            self.parent.folder, self.parent.flow_dataname))
        self.parent.data_grad.read_csv()
        self.parent.data_grad.x = np.array(
            self.parent.data_grad.data['I_M,mA'])[-10:]
        self.parent.data_grad.y = np.array(self.parent.data_grad.data['B,mTl'])[-10:]
        self.parent.data_grad.xlabel = 'I$_M$,mA'
        self.parent.data_grad.ylabel = 'B,mTl'
        self.parent.data_grad.xerr = 0.0035/100*self.parent.data_grad.x[-10:]
        self.parent.data_grad.yerr = 0.05*self.parent.data_grad.y[-10:]
        plt.figure(dpi=500, figsize=(8, 5))
        self.parent.data_grad.make_point_grafic()

        a, sigma = curve_fit(
            self.B, self.parent.data_grad.x/1000, self.parent.data_grad.y/10**3)
        sigma = abs(np.sqrt(np.diag(sigma))/a)
        eps = (np.min(sigma)**2+(0.0035/100)**2+0.02**2)**0.5
        print('fit',eps)
        x_range = np.arange(min(self.parent.data_grad.x),
                            max(self.parent.data_grad.x), step=0.001)
        y_fit = self.B(x_range/1000, a[0], a[1], a[2])*10**3
        plt.plot(x_range, y_fit)
        plt.savefig(os.path.join(
            self.parent.folder,
            self.parent.grad_chartname))
        return (a, eps)

    def make_main(self, a, eps_b):
        self.parent.main_chartname = 'Chart'
        self.parent.data_main = Data(data_filename=os.path.join(self.parent.folder, self.parent.dataname),
                                     saving=os.path.join(self.parent.folder, self.parent.main_chartname))
        self.parent.data_main.read_csv()

        h = self.parent.a
        e = -np.array((self.parent.data_main.data['U_34,mV'] -
                      self.parent.data_main.data['U_0,mV'])*10**3)
        print(e)
        b = np.array(
            self.B(self.parent.data_main.data['I_M,mA']/10**3, a[0], a[1], a[2]))
        print('i  ',self.parent.data_main.data['I_0,mA'])
        eds = chr(949)
        self.parent.data_main.x = np.array(
            self.parent.data_main.data['I_0,mA']*b)
        self.parent.data_main.y = e
        self.parent.data_main.ylabel = eds+'$_x$, мкV'
        self.parent.data_main.xlabel = 'I$_{обр} \cdot B$, мА$\cdot $ Tл'
        self.parent.data_main.make_grafic()
        self.parent.data_main.xerr = abs(
            self.parent.data_main.x*(eps_b**2+0.01**2)**0.5)
        self.parent.data_main.yerr = abs(5*10**-5*self.parent.data_main.y)
        self.parent.data_main.through_0 = 0
        k, b1, sigma = self.parent.data_main.make_grafic()
        k = k * 10**-6
        sigma[0]*=10**-6
        self.parent.R_H = k*h
        self.parent.sigma_R_H = self.parent.R_H*sigma[0]/k

        e_e = 1.6*10**-19
        self.parent.n = 1/(-self.parent.R_H*e_e)*10**-21
        self.parent.sigma_n = self.parent.n*abs(sigma[0]/k)

        self.parent.b = -self.parent.sigma*self.parent.R_H

        self.parent.sigma_b = self.parent.b*((self.parent.sigma_sigma/self.parent.sigma)**2 +
                                             (sigma[0]/k)**2)**0.5
        print(sigma[0]/ k)

    def make_text(self):
        s0 = 'Вычисленные постоянные равны:'+'\n' +\
            'R_X - постоянная Холла, '+'\n'+' n - концентрация носителей заряда,'+'\n' +\
             'sigma - удельная проводимость, '+'\n'+' b - подвижность'+'\n'+'\n'

        s1 = 'R_X = ' + str(int(round(self.parent.R_H*10**10, -1))) + '  +-  ' + \
            str(int(round(self.parent.sigma_R_H*10**10, -1))) + \
            ' , 10^-10 м^3/Кл'+'\n'+'\n'
        s2 = 'n = ' + str(int(round(self.parent.n, -1))) + '  +-  ' + \
            str(int(round(self.parent.sigma_n, -1))) + ' , 10^21  1/м^3'+'\n'+'\n'
        s3 = 'sigma = ' + str(round(self.parent.sigma)) + '  +-  ' + \
            str(round(self.parent.sigma_sigma)) + ', 1/(Ом*м)'+'\n'+'\n'

        s4 = 'b = ' + str(round(self.parent.b*10**4, 2)) + '  +-  ' + \
            str(round(self.parent.sigma_b*10**4, 2)) + ', см^2/(В*с)'+'\n'+'\n'
        
            
            
        return s0+s1+s2+s3+s4
