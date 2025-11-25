
import tldextract, sys, uuid, json, os, importlib, re, base64, traceback
#import logging
from urllib.parse import urlparse
BROWSER_PATH = os.environ["BROWSER_PATH"];
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QLayout, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QListWidget, QPushButton, QMessageBox
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QUrl, Slot, QObject;
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtNetwork import QNetworkProxy

from browser.api.project_helper import ProjectHelper;
from browser.ui.custom_web_engine_page import CustomWebEnginePage;
from browser.api.iplocation_helper import IPLocationHelper;

DEBUG_PORT = '5588'
DEBUG_URL = 'http://127.0.0.1:%s' % DEBUG_PORT
os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = DEBUG_PORT
HISTORY_FILE = "history.json"


class BrowserTab(QWidget):
    def __init__(self, browser, url=None, parent=None):
        super().__init__(parent)
        self.parent = parent;
        layout = QVBoxLayout()
        self.browser = browser;
        self.profile = self.browser.profile;
        self.url_bar = QLineEdit()
        self.url_bar.setMinimumWidth(800);
        self.url_bar.setPlaceholderText("Enter URL...")
        self.url_bar.textChanged.connect(self.show_suggestions)
        self.url_bar.returnPressed.connect(self.handle_enter_press)
        self.url_bar.keyPressEvent = self.handle_keypress
        self.history_list = QListWidget()
        self.history_list.hide()
        self.history_list.itemClicked.connect(self.select_history_item)
        self.history_list.itemActivated.connect(self.select_history_item)
        #os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = '--proxy-server="socks5://127.0.0.1:9050"';
        self.web_view = QWebEngineView();
        

        self.project_helper = ProjectHelper();
        self.web_view.setPage(CustomWebEnginePage(self.browser.profile, self))
        self.web_view.loadFinished.connect(self.on_load_finished_signal)
        self.web_view.page().urlChanged.connect(self.urlChanged_signal);

        #self.set_proxy_socks5();
        #self.set_proxy_http(ip="127.0.0.1", port=9051);
        # montar a barrinha com botoes==============
        ly = QHBoxLayout();
        
        bt1 = QPushButton("Inspector");
        ly.addWidget(bt1);
        bt1.clicked.connect(self.bt1_click);

        for project in self.project_helper.list():
            project.before_layout(ly);
        ly.addStretch(0)
        ly.setSizeConstraint(QLayout.SetFixedSize)
        widget1 = QWidget();
        widget1.setLayout( ly );

        ly2 = QHBoxLayout();
        ly2.addStretch(0)
        ly2.setSizeConstraint(QLayout.SetFixedSize)
        ly2.addWidget(self.url_bar);
        ly2.addWidget(widget1);
        widget2 = QWidget();
        widget2.setLayout( ly2 );
        layout.addWidget(widget2)
        #========================================
        layout.addWidget(self.history_list)
        layout.addWidget(self.web_view)
        self.setLayout(layout)
        self.web_view.urlChanged.connect(self.update_url_bar)
        self.url_bar.setFocus()  # Automatycznie ustawia fokus na polu URL
        if url != None:
            self.url_bar.setText(url);
            self.load_url();

    def validar_pais_inicio(self):
        js_settings = json.loads( open(os.environ["BROSER_DIR_SETTINGS_FILE_NAME"], "r").read() );
        if js_settings.get("block_country") != None and js_settings["block_country"].strip() != "":
            self.page_iplocation = IPLocationHelper(parent=self.parent);
            self.page_iplocation.loadFinished.connect(self.validar_pais_inicio_loadFinished);
            self.page_iplocation.get_country();
        else:
            self.validar_pais_inicio_text(json.dumps({"YourFuckingCountryCode" : None}));
    def validar_pais_inicio_loadFinished(self):
        self.page_iplocation.toPlainText(self.validar_pais_inicio_text);
    def validar_pais_inicio_text(self, data):
        js_test = json.loads(data);
        js_settings = json.loads( open(os.environ["BROSER_DIR_SETTINGS_FILE_NAME"], "r").read() );
        if js_settings.get("proxy") != None and js_settings.get("proxy").strip() != "" and os.path.exists(js_settings.get("proxy")):
            js_proxy = json.loads( open( js_settings.get("proxy"), "r" ).read() );
            js_settings["block_country"] = js_settings["block_country"] + js_proxy["block_country"];
        if js_test["YourFuckingCountryCode"] == None or not js_test["YourFuckingCountryCode"].lower() in js_settings["block_country"].lower():
            url = self.url_bar.text().strip()
            if not url.startswith("http"):
                url = "https://" + url
            self.web_view.setUrl(url)
            self.save_history(url)
            self.web_view.setFocus()
            self.history_list.hide()
        else:
            msgBox = QMessageBox();
            msgBox.setText( "Você não pode acessar pois está no país:" + js_test["YourFuckingCountryCode"] );
            msgBox.exec();

    def bt1_click(self):
        self.inspector = QWebEngineView()
        self.inspector.setWindowTitle('Web Inspector')
        self.inspector.load(QUrl(DEBUG_URL))
        self.web_view.page().setDevToolsPage(self.inspector.page())
        self.inspector.show()

    def urlChanged_signal(self, url):
        self.history_list.hide()
        if url.toString() not in self.browser.history:
            self.browser.history.append(url.toString())
        self.browser.save();

    def on_load_started_signal(self):
        pass;
    
    def callback_function(self, html):
        for project in self.project_helper.list():
            project.after_render( self.web_view.page(), html );
        extracted = tldextract.extract(self.url_bar.text());
        scripts = [];
        buffer_dir_files = os.path.join(os.environ["BROWSER_PATH"], "browser/resources", "scripts_block");
        buffer_files = os.listdir( buffer_dir_files );
        for i in range(len(buffer_files)):
            js = json.loads(open(os.path.join(buffer_dir_files, buffer_files[i]), "r").read());
            if js["active"] == True:
                scripts.append(js);
        for i in range(len(scripts)):
            regexp = re.compile( scripts[i]["url"] );
            if regexp.search(self.url_bar.text()):
                javascript = base64.b64decode(scripts[i]["script"]).decode();
                try:
                    self.web_view.page().runJavaScript(javascript);
                except:
                    traceback.print_exc();
        #This document requires 'TrustedHTML' assignment.
    def on_load_finished_signal(self, sucesso):
        self.history_list.hide(); # se carregar com sucesso uma página, então fecha o help de histórico
        self.atualizar_titulo_aba();
        self.web_view.page().runJavaScript("document.documentElement.outerHTML", self.callback_function);
        #self.web_view.page().runJavaScript('function abcde(){ return "Uma resposta de dentro da funcao javascript"; }\nabcde();', self.__callback);
        #self.web_view.page().runJavaScript( js_back, self.callback_function );
    def __callback(self, response):
        if response:
            print ("Handling JS response: %s", response)
    
    def handle_enter_press(self):
        if self.history_list.isVisible() and self.history_list.count() > 0:
            self.select_history_item(self.history_list.item(0))  # Select top result
        else:
            self.load_url();
        self.history_list.hide()
    
    def load_url(self):
        self.validar_pais_inicio();
    #    url = self.url_bar.text().strip()
    #    if not url.startswith("http"):
    #        url = "https://" + url
    #    self.web_view.setUrl(url)
    #    #backend = Backend()
    #    #self.webchannel = QWebChannel(self)
    #    #self.webchannel.registerObject("backend", backend)
    #    #self.web_view.page().setWebChannel(self.webchannel)
    #    self.save_history(url)
    #    self.web_view.setFocus()
    #    self.history_list.hide()
    
    def atualizar_titulo_aba(self):
        extracted = tldextract.extract(self.url_bar.text());
        index = -1;
        for i in range(self.browser.tabs.count()):
            if self.browser.tabs.widget(i) == self:
                index = i;
                break;
        if index >= 0:
            self.browser.tabs.setTabText( index , extracted.domain[0:20]);
    
    def update_url_bar(self, url):
        url = url;
        if type(url) != type(""):
            url = url.toString();
        self.url_bar.setText(url);
        self.url_bar.setCursorPosition(0);
    
    def save_history(self, url):
        pass;
    
    def show_suggestions(self):
        text = self.url_bar.text().lower()
        suggestions = [url for url in self.browser.history if url.lower().find(text.lower()) >= 0 ]
        self.history_list.hide();
        if suggestions:
            if len(suggestions) == 0:
                self.history_list.hide()
            else:
                self.history_list.clear()
                self.history_list.addItems(suggestions)
                self.history_list.setFixedHeight(min(len(suggestions) * 20, 200))
                self.history_list.show()
    
    def select_history_item(self, item):
        self.url_bar.setText(item.text())
        self.load_url()
    
    def handle_keypress(self, event):
        if event.key() == Qt.Key_Down and self.history_list.isVisible():
            self.history_list.setFocus()
            self.history_list.setCurrentRow(0)
        else:
            QLineEdit.keyPressEvent(self.url_bar, event)
