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
        self.parent.chartname = 'Chart'
        self.parent.data = Data(data_filename=os.path.join(self.parent.folder, self.parent.dataname),
                                saving=os.path.join(self.parent.folder, self.parent.chartname))
        self.parent.data.read_csv()
        # add B(I_M) #TODO
        self.parent.data.x = np.array(self.parent.data.data['I_0,mA'])*np.array(self.parent.data.data['I_M,mA'])
        self.parent.data.y = self.parent.data.data['U_34,mV']
        self.parent.data.ylabel = 'U_34,mV'
        self.parent.data.xlabel = 'I$_{обр} \cdot B$, мА$\cdot $ Tл'
        self.parent.data.make_grafic()

        self.setWindowTitle('Основной эксперимент. Обработка данных')
        self.resize(1400, 800)

        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)

        pixmap = QPixmap(os.path.join(
            self.parent.folder, self.parent.chartname))
        self.label = QLabel(self)
        self.label.setScaledContents(True)
        self.label.setFixedSize(0.7*self.width(), 0.9*self.height())
        self.label.setPixmap(pixmap)

        self.text = QTextBrowser()
        self.text.setText('text')

        self.hbox_layout = QGridLayout(self.centralwidget)
        self.hbox_layout.addWidget(self.label, 0, 0)
        self.hbox_layout.addWidget(self.text, 0, 1)