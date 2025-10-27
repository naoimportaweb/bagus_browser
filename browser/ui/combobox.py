import os, sys, inspect, json;

from PySide6.QtCore import (Qt)
from PySide6.QtWidgets import (QWidget, QComboBox, QHBoxLayout, QVBoxLayout)

class ComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent);
        self.lista = [];
    def add(self, text, value):
        self.addItem(text);
        self.lista.append( value );