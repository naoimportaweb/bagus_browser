import tldextract, sys, uuid, json, os, importlib, traceback

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QTextEdit, QWidget, QTabWidget, QPushButton, QMessageBox, QTabWidget
from PySide6.QtCore import Qt

from browser.ui.table import *
from browser.api.myass_helper import *

class PanelMyassWorkflow(QWidget):
    def __init__(self, parent):
        super().__init__(parent);
        self.parent_ = parent;
        self.table = Table.widget_tabela(self.parent_, ["name", "status"]); 
        layout = QVBoxLayout();
        layout.addWidget(self.table);
        btn_atualizar = QPushButton("Atualizar");
        layout.addWidget(btn_atualizar);
        btn_atualizar.clicked.connect(self.btn_atualizar_click);
        self.setLayout(layout);
        self.btn_atualizar_click();
    def btn_atualizar_click(self):
        self.page = MyassHelper(parent=self.parent_);
        self.page.loadFinished.connect(self._loadFinished);
        self.page.post("service/workflow_list.php", {  });
    def _loadFinished(self):
        self.page.toPlainText(self.callable_text);
    def callable_text(self, data):
        self.html = data;
        js = json.loads( data );
        self.page.config["workflow"] = js;
        self.page.save_config();
        for i in range(len(js)):
            js[i]["status_text"] = "Active (running)";
            if not js[i]["status"]:
                js[i]["status_text"] = "Inactive"; 
            self.table.add([js[i]["name"], js[i]["status_text"]], js[i])