import os, sys, traceback, json, base64;

from PySide6.QtCore import QByteArray, QUrl
from PySide6.QtWebEngineCore import  QWebEngineHttpRequest, QWebEnginePage

from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QTextEdit, QHBoxLayout, QWidget, QTabWidget, QListWidget, QPushButton, QButtonGroup, QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize,  QByteArray, QUrl, Signal
from PySide6.QtWebEngineCore import QWebEngineHttpRequest, QWebEnginePage

from browser.api.aes_helper import *

#Vocë tem que criar o arquivo ~/bagus/myass.jso e escrever:
#{
#        "url" : "https://wellington.tec.br/myass/",
#        "token" : "UmaChaveSimetrica",
#        "name"  : "publico",
#        "key"   : "UmaChaveSimetric"
#        "algorithm" : "AES-256"
#}

class MyassHelper(QWebEnginePage):
    returned = Signal(object)
    def __init__(self, parent=None):
        super().__init__(parent=parent);
        self.path_config = os.path.join(os.path.expanduser("~/bagus/"), "myass.json");
        self.config = None;
        if not os.path.exists(self.path_config):
            self.config = {"url" : "https://wellington.tec.br/myass/", "token" : "UmaChaveSimetrica",  "name"  : "publico", "key"   : "UmaChaveSimetric", "algorithm" : "AES-256" };
            with open(self.path_config, "w") as f:
                f.write( json.dumps( self.config, ensure_ascii=False ) );
        else:
            self.config = json.loads( open(self.path_config, "r").read() );

    def load_config(self):
        self.path_config = os.path.join(os.path.expanduser("~/bagus/"), "myass.json");
        self.config = json.loads( open(self.path_config, "r").read() );
    def save_config(self):
        self.path_config = os.path.join(os.path.expanduser("~/bagus/"), "myass.json");
        with open(self.path_config, "w") as f:
            f.write( json.dumps( self.config, ensure_ascii=False ) );

    def decrypt_text(self, data):
        self.path_config = os.path.join(os.path.expanduser("~/bagus/"), "myass.json");
        self.config = json.loads( open(self.path_config, "r").read() );
        return decrypt_aes_cbc_no_iv(self.config["key"] ,  data );
    
    def decrypt_array(self, data, fields):
        self.load_config();
        for i in range(len(data)):
            for k in range(len(fields)):
                if data[i].get( fields[k] ) != None and data[i].get( fields[k] ) != "" :
                    data[i][fields[k]] = decrypt_aes_cbc_no_iv(self.config["key"] , data[i][fields[k]] );
        return data;
    def create_work(self, unique_id, workflow, data):
        self.load_config();
        workflow = encrypt_aes_cbc_no_iv(self.config["key"] , workflow );
        return self.post("service/work_create_execution.php", data, envelop={"workflow" : workflow, "unique_name" : unique_id});
    
    def post(self, url, data, envelop={}):
        self.path_config = os.path.join(os.path.expanduser("~/bagus/"), "myass.json");
        self.config = json.loads( open(self.path_config, "r").read() );
        envelop["device"] = self.config["name"];
        envelop["service_token"]    = self.config["token"];
        envelop["data"] = encrypt_aes_cbc_no_iv(self.config["key"] , json.dumps(data) );
        url = QUrl.fromUserInput(self.config["url"] + url); 
        request = QWebEngineHttpRequest();
        request.setUrl( url );
        request.setMethod(QWebEngineHttpRequest.Post);
        request.setHeader(QByteArray(b'User-Agent'), QByteArray(b'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0'));
        request.setHeader(QByteArray(b'Content-Type'),QByteArray(b'application/json'))
        request.setPostData(json.dumps(envelop).encode("utf-8")); #
        retorno = request.postData();
        self.load(request)
