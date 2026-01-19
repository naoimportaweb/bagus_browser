import os, sys, traceback, json, re, uuid, hashlib;

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QMessageBox, QComboBox, QLayout, QDialog, QGridLayout, QTextEdit, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QTabWidget, QListWidget, QPushButton, QButtonGroup, QToolBar
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings, QWebEngineUrlRequestInterceptor
from urllib.parse import urlparse
from datetime import datetime

from browser.api.myass_helper import *

class Myass():
    def __init__(self):
        self.page = None;
        self.html = None;
        self.url  = None;
        self.config = None;
        self.path_config = os.path.join(os.path.expanduser("~/bagus/"), "myass.json");
        if os.path.exists(self.path_config):
            self.config = json.loads( open(self.path_config, "r").read() );
        pass;
    
    def after_render(self, page, html):
        self.page = page;
        self.html = html;
        self.url = page.url().toString();
        javascript = 'console.log("Texto obtido pela extensão Myass");';
        page.runJavaScript(javascript);

    def before_layout(self, layout_button_group):
        self.bt1 = QPushButton("Myass");
        layout_button_group.addWidget(self.bt1);
        self.bt1.clicked.connect(self.bt1_click);
    
    def bt1_click(self):
        if self.config == None:
            msgBox = QMessageBox();
            msgBox.setText("Configure MyAss.");
            msgBox.exec();
            return;
        f = FormMyass(self.html, self.url, self.config);
        f.exec_();

class FormMyass(QDialog):
    def __init__(self, html, url, config):
        super().__init__();
        self.html = html;
        self.url = url;
        self.config = config;
        self.page = MyassHelper(parent=self);
        self.resize(600, 320);
        self.diretorio = None;
        self.layout = QGridLayout();
        self.layout.setContentsMargins(20, 20, 20, 20);
        self.layout.setSpacing(10);
        itens = [""];
        if self.page.config.get("workflow") != None:
            for workflow in self.page.config.get("workflow"):
                if workflow["status"]:
                    itens.append( workflow["name"] );
        self.combobox2 = QComboBox();
        self.combobox2.addItems(itens);
        self.combobox2.currentTextChanged.connect(self.combobox2_text_changed)
        self.layout.addWidget(self.combobox2, 0, 0, 1, 3)
        
        self.widget_layout = QWidget();
        self.layout.addWidget(self.widget_layout, 1, 0, 1, 3);

        self.myass_elements = [];
        btn_myass = QPushButton("Send to MyAss")
        btn_myass.clicked.connect(self.start_myass_click)
        self.layout.addWidget(btn_myass, 4, 1);
        self.setStyleSheet(self.load_styles());
        self.setLayout(self.layout)
    def criar_layout_inicial(self):
        self.myass_elements = [];
        self.layout_campos = QVBoxLayout();
        self.widget_layout.setLayout( self.layout_campos );

    def criar_layout(self, layout_root, element):
        for child in element["elements"]:
            if child["type"] == "text":
                input_element = QTextEdit();
                layout_root.addWidget(input_element);
                self.myass_elements.append({"input" : input_element, "child" : child});
                if child.get("data") != None and child["data"].get("html") != None:
                    texto_buffer = "";
                    for data_get in child["data"]["html"]:
                        find_item_type = data_get.split(":")[0];
                        if texto_buffer.strip() != "":
                            texto_buffer += " - ";
                        if find_item_type == "regex":
                            compiled = re.compile( data_get.split(":")[2] );
                            list_result = compiled.findall(self.html);
                            if len(list_result) > 0:
                                if data_get.split(":")[1] == "*":
                                    texto_buffer += "  ".join( list_result );
                                else:
                                    texto_buffer += "  " + list_result[int(data_get.split(":")[1])];
                        elif find_item_type == "url":
                            texto_buffer += self.url;
                    input_element.setPlainText( texto_buffer.strip() );
            elif child["type"] == "panel":
                layout = QVBoxLayout();
                widget1 = QWidget();
                widget1.setLayout( layout );
                layout_root.addWidget(widget1);
                self.criar_layout(layout, child);

    def combobox2_text_changed(self, text):
        text_input = "";
        self.criar_layout_inicial();
        if self.combobox2.currentIndex() > 0:
            index = self.combobox2.currentIndex() - 1;
            workflow = self.page.config["workflow"][index];
            form_input = workflow["form"]["input"];
            if form_input != None:
                for element in form_input["elements"]:
                    self.criar_layout(self.layout_campos, element);
    def _loadFinished(self):
        self.page.toPlainText(self.callable_text);
    
    def callable_text(self, data):
        js = json.loads( data );
        if js["status"] == 1:
            msgBox = QMessageBox();
            msgBox.setText("Myass Sucess");
            msgBox.exec();
            self.close();
        else:
            msgBox = QMessageBox();
            msgBox.setText("Error: " + js["msg"]);
            msgBox.exec();
    def send_server(self, envelope):
        try:
            self.page.loadFinished.connect(self._loadFinished);
            self.page.create_work( hashlib.md5((self.url + datetime.today().strftime('%Y-%m-%d') + self.config["name"] ).encode()).hexdigest(), envelope["data"]["workflow"], envelope);
        except:
            msgBox = QMessageBox();
            msgBox.setText("MyAss connection error!!!");
            msgBox.exec();
            traceback.print_exc();
    def send_server_combo(self):
        index = self.combobox2.currentIndex();
        if index > 0:
            index = index - 1;
            dados = {};
            for element in self.myass_elements:
                if element["child"].get("data") != None:
                    if element["child"]["type"] == "text":
                        dados[element["child"]["data"]["field"]] = element["input"].toPlainText();
            dados = {"_id" : str(uuid.uuid4()), "workflow" : self.page.config["workflow"][index]["name"], "work" : dados }
            context = {"url" : self.url, "name" : "resposta_" + hashlib.md5(self.url.encode()).hexdigest(), "input" : dados};
            envelope = {"data" : dados, "context" : context}
            return self.send_server(envelope);
        # if cindex == 1:
        #     dados = {"_id" : str(uuid.uuid4()), "workflow" : "cve", "work" : {"texto" : self.textEdit.toPlainText()} }
        #     context={"file" : "", "url" : self.url, "name" : "resposta_" + hashlib.md5(self.url.encode()).hexdigest(), "directory" : os.path.expanduser("~/Desktop") };
        #     envelope = {"data" : dados, "context" : context}
        #     return self.send_server(envelope);
        # if cindex == 2:
        #     name_url = self.url.split("/")[-1];
        #     dados = {"_id" : str(uuid.uuid4()), "workflow" : "malpedia", "work" : {"name_url" : name_url} }
        #     context={"name" : name_url, "url" : self.url, "directory" : os.path.expanduser("~/tmp/cml")};
        #     envelope = {"data" : dados, "context" : context}
        #     return self.send_server(envelope);
        # if cindex == 3:
        #     channel = self.textEdit.toPlainText().split("\n")[0].strip();
        #     user = self.textEdit.toPlainText().split("\n")[1].strip();
        #     channel_id = self.textEdit.toPlainText().split("\n")[2].strip();
        #     dados = {"_id" : str(uuid.uuid4()), "workflow" : "youtuber", "work" : {"url" : channel, "username" : user, "channel" : channel_id } }
        #     context={"url" : channel, "username" : user, "channel" : channel_id, "report" : {"directory" : "/tmp", "filename" : channel_id + datetime.today().strftime('%Y-%m-%d')} };
        #     envelope = {"data" : dados, "context" : context}
        #     return self.send_server(envelope);
        return None;
    def start_myass_click(self):
        retorno = self.send_server_combo();
        if retorno != None:
            if retorno["status"] == 1:
                self.close();
            else:
                msgBox = QMessageBox();
                msgBox.setText(  retorno["msg"] );
                msgBox.exec();
                traceback.print_exc();
    def load_styles(self):
        return open( os.path.join( BROWSER_PATH, "browser", "resources", "style.txt" ), "r" ).read();