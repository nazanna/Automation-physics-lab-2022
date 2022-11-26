#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 21:31:55 2022

@author: anna
"""

from PyQt6.QtWidgets import (QPushButton,
                             QWidget,
                             QGridLayout,
                             QLabel,
                             QLineEdit
                             )
from Abstract_window import AbstractWindow
import time


class ResistanceWindow(AbstractWindow):
    def __init__(self, parent):
        super().__init__()
    
        self.setWindowTitle('Определение удельной проводимости')
        self.parent = parent
        
        self.start = QPushButton('Старт')
        self.start.clicked.connect(self.start_clicked)
        self.start.setEnabled(False)
    
        self.menu = QPushButton('Меню')
        self.menu.setEnabled(False)
        self.menu.clicked.connect(self.menu_clicked)
        
        self.current = QLabel('Ток через образец: ', self)
        self.voltage= QLabel('Напряжение на 3_5: ', self)
        self.current_value = QLabel(self)
        self.voltage_value = QLabel(self)
        
        self.line_L = QLineEdit(placeholderText='Введите L_35, мм')
        self.line_L.returnPressed.connect(self.enter_L)
        
        self.line_l = QLineEdit(placeholderText='Введите l, мм')
        self.line_l.returnPressed.connect(self.enter_l)
                
        self.centralwidget = QWidget()
        self.resize(1400, 800)
        self.setCentralWidget(self.centralwidget)
        self.grid_layout = QGridLayout(self.centralwidget)
        
        self.grid_layout.addWidget(self.line_L, 0, 0)
        self.grid_layout.addWidget(self.line_l, 0, 1)
        self.grid_layout.addWidget(self.start, 1, 0, 1, -1)
        self.grid_layout.addWidget(self.current, 2, 0)
        self.grid_layout.addWidget(self.current_value, 2, 1)
        self.grid_layout.addWidget(self.voltage, 3, 0)
        self.grid_layout.addWidget(self.voltage_value, 3, 1)
        self.grid_layout.addWidget(self.menu, 4, 0, 1, -1)
        
    def menu_clicked(self):
        self.parent.number = 0
        self.parent.change_number()
    
    def enter_L(self):
        self.parent.L=float(self.line_L.text())/1000
        self.line_L.setReadOnly(True)
        
    def enter_l(self):
        self.parent.l=float(self.line_l.text())/1000
        self.start.setEnabled(True)
        self.line_l.setReadOnly(True)
    
    def start_clicked(self):
        self.start.setEnabled(False)
        current=10
        voltage=15
        # voltage, current = self.measure()
        print(voltage*self.parent.l*self.parent.a)
        print(current*self.parent.L)
        
        self.parent.sigma = current*self.parent.L/(voltage*self.parent.l*self.parent.a)
        self.parent.sigma_sigma = self.parent.sigma*((5*10**-5)**2+(0.0035/100)**2)**0.5
        self.current_value.setText(str(current)+', mA')
        self.voltage_value.setText(str(voltage)+', mV')
        self.menu.setEnabled(True)
        
    def measure(self):
        
        msg = 'VOLTage '+str(1)+'\n'
        self.parent.ser.write(msg.encode('ascii'))
        time.sleep(1)
        
        
        
        f_amp = open(self.parent.amp_name, 'w')
        f_amp.write('Measure:Current:DC?\n')
        f_amp.close()
        f_amp = open(self.parent.amp_name, 'r')
        a = '{:.9f}'.format(float(f_amp.read(15))*10**3)
        f_amp.close()
        
        f_amp.close()
        f_volt = open(self.parent.volt_name, 'w')
        f_volt.write('Measure:Voltage:DC?\n')
        f_volt.close()
        f_volt = open(self.parent.volt_name, 'r')
        v = '{:.9f}'.format(float(f_volt.read(15))*10**3)
        f_volt.close()
        return float(v), float(a)
    

    def closeEvent(self, event):
        self.parent.close()