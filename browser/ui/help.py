import os, sys, inspect, json;

from PySide6.QtCore import (QByteArray, QFile, QFileInfo, QSettings, QSaveFile, QTextStream, Qt, Slot)
from PySide6.QtWidgets import (QWidget, QLineEdit, QMessageBox, QTextEdit, QDialog, QLabel, QGridLayout, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout)

def QLineWidget(layout, controls, stretch_inicio=False, stretch_fim=False):
    widget1 = QWidget();
    widget1_layout = QHBoxLayout();
    widget1.setLayout(widget1_layout);
    if stretch_inicio:
        widget1_layout.addStretch();
    for control in controls:
        if type(control).__name__ == type("").__name__:
            widget1_layout.addStretch();
            continue;
        widget1_layout.addWidget( control );
    if stretch_fim:
        widget1_layout.addStretch();
    layout.addWidget(widget1);