import tldextract, sys, uuid, json, os, importlib, traceback

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QTextEdit, QWidget, QTabWidget, QPushButton, QMessageBox, QTabWidget
from PySide6.QtCore import Qt

class PanelSettingsSelected(QWidget):
    def __init__(self, parent):
        super().__init__(parent);
        self.parent_ = parent;
        layout = QVBoxLayout();
        self.setLayout(layout);
