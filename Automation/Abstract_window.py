#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 19:52:27 2022

@author: anna
"""

from PyQt6.QtWidgets import (QMainWindow,
                             QMenu)

from PyQt6.QtGui import QAction

class AbstractWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.create_actions()
        self.create_menuBar()

    def create_menuBar(self):
        menuBar = self.menuBar()
        self.fileMenu = QMenu("&Файл", self)
        menuBar.addMenu(self.fileMenu)
        self.helpMenu = QMenu("&Помощь")
        menuBar.addMenu(self.helpMenu)
        self.fileMenu.addAction(self.exitAction)
        self.helpMenu.addAction(self.helpContentAction)
        self.helpMenu.addAction(self.aboutAction)

    def create_actions(self):
        self.exitAction = QAction("&Выход", self)
        self.exitAction.triggered.connect(self.exit_click)
        self.helpContentAction = QAction("&Инструкция", self)
        self.helpContentAction.triggered.connect(self.help_click)
        self.aboutAction = QAction("&О программе", self)
        self.aboutAction.triggered.connect(self.about_click)

    def exit_click(self):
        self.close()

    def help_click(self):
        print('Help')
        # TODO

    def about_click(self):
        print('About')
        # TODO