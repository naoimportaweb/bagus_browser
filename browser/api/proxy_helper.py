import tldextract, sys, uuid, json, os, importlib, traceback, re;

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from PySide6.QtNetwork import QNetworkProxy
#from PySide6.QtWidgets import QDialog, QWidget, QMessageBox
from PySide6.QtCore import Qt

class ProxyHelper:
    def __init__(self):
        pass;
    def set_proxy(self, proxy_config_path):
        if proxy_config_path == None or proxy_config_path == "" or not os.path.exists(proxy_config_path):
            return;
        proxy_js = json.loads( open(proxy_config_path, "r").read() );
        itens = proxy_js["url"].split(":");
        if itens[0] == "http":
            self.set_proxy_http(ip=itens[1].replace("//", ""), port=int(itens[2]));
        elif itens[0] == "socks5":
            self.set_proxy_socks5(ip=itens[1].replace("//", ""), port=int(itens[2]));
    def clean_proxy(self):
        self.set_proxy_clear();
    def set_proxy_socks5(self, ip="127.0.0.1", port=9050):
        proxy = QNetworkProxy();
        proxy.setType(QNetworkProxy.Socks5Proxy);
        proxy.setHostName( ip   );
        proxy.setPort(     port );
        QNetworkProxy.setApplicationProxy(proxy);

    def set_proxy_http(self, ip="127.0.0.1", port=8080):
        proxy = QNetworkProxy()
        proxy.setType(QNetworkProxy.HttpProxy)
        proxy.setHostName( ip   );
        proxy.setPort(     port );
        QNetworkProxy.setApplicationProxy(proxy)

    def set_proxy_clear(self):
        proxy = QNetworkProxy()
        proxy.setType(QNetworkProxy.NoProxy)
        QNetworkProxy.setApplicationProxy(proxy)