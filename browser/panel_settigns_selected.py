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
        template_js = json.loads( open(self.DIR_SETTINGS_TEMPLATE, "r").read() );
        template_js["elements"][0]["database"]["file"] =  os.environ["BROSER_DIR_SETTINGS_FILE_NAME"];
        template_js["elements"][0]["elements"][0]["font"]["directory"] = os.path.join( os.environ["USER_BROWSER_PATH"], os.environ["BROWSER_CONFIG"], "proxy" );
        self.dw = DataWidget( template_js, callback=self.data_widget_save );
        layout.addWidget(self.dw);
        self.setLayout(layout);
    
    def reload_data(self):
        self.dw.reload_data();
    
    def data_widget_save(self, data):
        if data != None:
            proxy_config_path = data[0]["proxy"]; 
            ph = ProxyHelper();
            if proxy_config_path != None and proxy_config_path != "":
                msg = "Attention: If you have modified the proxy, it is recommended that you close the windows of the Browser tab.";
                ph.set_proxy(proxy_config_path);
                msgBox = QMessageBox();
                msgBox.setText( msg );
                msgBox.exec();
            else:
                reply = QMessageBox.question(self, "Proxy", "Are you aware that you have just disabled the Proxy?", QMessageBox.Yes | QMessageBox.No);
                if reply == QMessageBox.Yes:
                    ph.clean_proxy();
