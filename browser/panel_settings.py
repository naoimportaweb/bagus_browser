import sys, uuid, json, os, traceback

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QWidget, QTabWidget, QPushButton, QMessageBox
from PySide6.QtCore import Qt

from browser.ui.table import *
from browser.form_navigation_script import FormNavigationScript;
from browser.ui.help import *
from browser.form_generic import FormGeneric;
from browser.panel_settigns_selected import PanelSettingsSelected;

class PanelSettings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent);
        self.parent_ = parent;
        self.DIR_PROXY = os.path.join( os.environ["USER_BROWSER_PATH"], os.environ["BROWSER_CONFIG"], "proxy" );
        if not os.path.exists( self.DIR_PROXY ):
            os.makedirs( self.DIR_PROXY );
        self.DIR_PROXY_TEMPLATE = os.path.join( BROWSER_PATH, "browser", "resources", "template", "proxy.json" );
        self.tab_settings = QTabWidget();
        self.tab_settings.setTabsClosable(False);
        self.tab_settings.setDocumentMode(True);
        self.tab_settings_selected = PanelSettingsSelected(self);
        self.tab_settings.addTab(self.tab_settings_selected, "Selected")
        self.tab_settings_proxy = QWidget()
        self.tab_settings.addTab(self.tab_settings_proxy,    "Proxy")
        self.tab_settings.currentChanged.connect(self.tab_settings_currentChanged);
        layout = QVBoxLayout();
        layout.addWidget(self.tab_settings);
        self.setLayout(layout);
        self.tab_settigns_proxy_table = Table.widget_tabela(self.parent_, ["name", "url"], double_click=self.tab_settigns_proxy_table_click);
        btn_add = QPushButton("New proxy");
        btn_add.clicked.connect(self.btn_add_click);
        layout = QVBoxLayout();
        layout.addWidget(  self.tab_settigns_proxy_table);
        QLineWidget(layout, [btn_add], stretch_inicio=True);
        self.tab_settings_proxy.setLayout( layout );
    def tab_settings_currentChanged(self, index):
        if index == 0:
            self.tab_settings_selected.reload_data();
    def reload_data(self):
        self.load_proxys();
        self.tab_settings_selected.reload_data();
    def load_proxys(self):
        files = os.listdir( self.DIR_PROXY );
        self.tab_settigns_proxy_table.cleanList();
        for file in files:
            file_js = json.loads( open( os.path.join( self.DIR_PROXY, file ), "r" ).read() );
            self.tab_settigns_proxy_table.add( [file_js["name"], file_js["url"]],  os.path.join( self.DIR_PROXY, file ) );
    def tab_settigns_proxy_table_click(self, file_path):
        path = self.tab_settigns_proxy_table.lista[self.tab_settigns_proxy_table.currentRow()];
        template_js = json.loads( open(self.DIR_PROXY_TEMPLATE, "r").read() );
        template_js["elements"][0]["database"]["file"] = path;
        f = FormGeneric(template_js, "Proxy config");
        f.exec();
        self.load_proxys();
        pass
    def btn_add_click(self):
        id_ = str(uuid.uuid4());
        template_js = json.loads( open(self.DIR_PROXY_TEMPLATE, "r").read() );
        template_js["elements"][0]["database"]["file"] = os.path.join(self.DIR_PROXY, id_ + ".json");
        f = FormGeneric(template_js, "Proxy config");
        f.exec();
        self.load_proxys();
        pass;