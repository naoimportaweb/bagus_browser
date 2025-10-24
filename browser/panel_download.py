import sys, uuid, json, os, traceback

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QWidget, QTabWidget, QPushButton, QMessageBox
from PySide6.QtCore import Qt, QProcess

from browser.ui.table import *

class PanelDownload(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent);
        self.parent_ = parent;
        self.table = Table.widget_tabela(self.parent_, ["URL", "File", "Status"], double_click=self.table_double_click);
        layout = QVBoxLayout();
        layout.addWidget(self.table);
        btn_atualizar = QPushButton("Atualizar");
        layout.addWidget(btn_atualizar);
        btn_atualizar.clicked.connect(self.btn_atualizar_click);
        self.setLayout(layout);

    def table_double_click(self):
        pass;
    def btn_atualizar_click(self):
        pass;

#p = QProcess()
#p.start("<program>", [<arguments>])