import os, sys, inspect, json;

from PySide6.QtCore import (QByteArray, QFile, QFileInfo, QSettings, QSaveFile, QTextStream, Qt, Slot)
from PySide6.QtWidgets import (QWidget, QLineEdit, QMessageBox, QTextEdit, QDialog, QLabel, QGridLayout, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout)

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from browser.ui.data_widget import DataWidget;

class FormGeneric(QDialog):
    def __init__(self, layout_js, title):
        super().__init__()
        self.resize(800, 600);
        self.setWindowTitle(title);
        dw = DataWidget(layout_js);
        self.layout = QVBoxLayout();
        self.layout.addWidget(dw);
        self.setLayout(self.layout);
        self.btn_close = QPushButton("Close");
        self.btn_close.clicked.connect(self.btn_close_click);
        self.setStyleSheet(self.load_styles());
    def btn_close_click(self):
        self.close();
    def load_styles(self):
        return open( os.path.join( BROWSER_PATH, "browser", "resources", "style.txt" ), "r" ).read();
    
    
