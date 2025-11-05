import os, sys, traceback, json, base64;

from PySide6.QtCore import QByteArray, QUrl
from PySide6.QtWebEngineCore import  QWebEngineHttpRequest, QWebEnginePage

from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QTextEdit, QHBoxLayout, QWidget, QTabWidget, QListWidget, QPushButton, QButtonGroup, QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize,  QByteArray, QUrl, Signal
from PySide6.QtWebEngineCore import QWebEngineHttpRequest, QWebEnginePage

from browser.api.aes_helper import *

##https://wtfismyip.com/json
#{
#  "YourFuckingIPAddress": "82.149.76.10",
#  "YourFuckingLocation": "San Juan, Puerto Rico",
#  "YourFuckingHostname": "82.149.76.10",
#  "YourFuckingISP": "Datacamp Limited",
#  "YourFuckingTorExit": false,
#  "YourFuckingCity": "San Juan",
#  "YourFuckingCountry": "Puerto Rico",
#  "YourFuckingCountryCode": "PR"
#}


class IPLocationHelper(QWebEnginePage):
    returned = Signal(object)
    def __init__(self, parent=None):
        super().__init__(parent=parent);

    def get_country(self):
        js = self.get("https://wtfismyip.com/json");
    
    def get(self, url):
        url = QUrl.fromUserInput(url); 
        request = QWebEngineHttpRequest();
        request.setUrl( url );
        request.setMethod(QWebEngineHttpRequest.Get);
        request.setHeader(QByteArray(b'User-Agent'), QByteArray(b'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0'));
        request.setHeader(QByteArray(b'Content-Type'),QByteArray(b'application/json'))
        #request.setPostData(json.dumps(envelop).encode("utf-8")); #
        #retorno = request.postData();
        self.load(request)
