import tldextract, sys, uuid, json, os, importlib, traceback, re;

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QTextEdit, QWidget, QTabWidget, QPushButton, QMessageBox, QTabWidget
from PySide6.QtCore import Qt

from browser.ui.data_widget import DataWidget;
from browser.api.proxy_helper import ProxyHelper
class PanelSettingsSelected(QWidget):
    def __init__(self, parent):
        super().__init__(parent);
        self.parent_ = parent;
        layout = QVBoxLayout();
        self.DIR_SETTINGS_TEMPLATE = os.path.join( os.environ["BROWSER_PATH"], "browser", "resources", "template", "selected.json" );
        #self.DIR_ SETTINGS_FILE_NAME = os.path.join( os.environ["USER_BROWSER_PATH"], os.environ["BROWSER_CONFIG"], "settings.selected.json" );
        template_js = json.loads( open(self.DIR_SETTINGS_TEMPLATE, "r").read() );
        template_js["elements"][0]["database"]["file"] =  os.environ["BROSER_DIR_SETTINGS_FILE_NAME"];
        template_js["elements"][0]["elements"][0]["font"]["directory"] = os.path.join( os.environ["USER_BROWSER_PATH"], os.environ["BROWSER_CONFIG"], "proxy" );
        dw = DataWidget( template_js, callback=self.data_widget_save );
        layout.addWidget(dw);
        self.setLayout(layout);

    def data_widget_save(self, data):
        if data != None:
            proxy_config_path = data[0]["proxy"]; 
            ph = ProxyHelper();
            if proxy_config_path != None and proxy_config_path != "":
                ph.set_proxy(proxy_config_path);
            else:
                ph.clean_proxy();
                
        pass;
