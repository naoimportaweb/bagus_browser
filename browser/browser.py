import tldextract, sys, uuid, json, os, importlib

BROWSER_PATH = os.environ["BROWSER_PATH"];
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

from browser.panel_myass import PanelMyass;
from browser.panel_navigation import PanelNavigation;
from browser.panel_download import PanelDownload;
from browser.panel_play import PanelPlay;
from browser.ui.private_profile import PrivateProfile;
from browser.api.analyze import Analyze;
from browser.ui.browser_tab import BrowserTab;
from browser.panel_settings import PanelSettings;

HISTORY_FILE = "history.json"

def is_valid_url(url):
    import re
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)


class Browser(QMainWindow):
    def __init__(self, path):
        super().__init__();
        self.path = path;
        self.config = json.loads( open( os.path.join( self.path, "config.json" ), "r" ).read() );
        self.analyze = Analyze();
        self.setWindowTitle("Bagus Browser")
        self.tab_principal = QTabWidget();
        self.tab_principal.setTabsClosable(False);
        self.tab_principal.setDocumentMode(True);
        self.tab_page_browser = QWidget()
        self.tab_principal.addTab(self.tab_page_browser,    "Browser")
        self.tab_page_download = PanelDownload()
        self.tab_principal.addTab(self.tab_page_download,   "Download")
        self.tab_page_navigate = PanelNavigation()
        self.tab_principal.addTab(self.tab_page_navigate,   "Navigation")
        self.tab_page_myass = PanelMyass(parent=self)
        self.tab_principal.addTab(self.tab_page_myass,      "MyAss")
        self.tab_page_disroot = QWidget()
        self.tab_principal.addTab(self.tab_page_disroot,    "Disroot")
        self.tab_page_play = PanelPlay()
        self.tab_principal.addTab(self.tab_page_play,       "Play")
        self.tab_page_xmpp = QWidget()
        self.tab_principal.addTab(self.tab_page_xmpp,       "XMPP Chat")
        self.tab_page_extension = QWidget()
        self.tab_principal.addTab(self.tab_page_extension,  "Extension")
        self.tab_page_settings = PanelSettings()
        self.tab_principal.addTab(self.tab_page_settings,  "Settings")
        self.tab_principal.setTabPosition(QTabWidget.TabPosition.West);
        self.setCentralWidget(self.tab_principal)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(False)  # Disable close buttons
        self.tabs.setDocumentMode(True)
        self.profile = PrivateProfile(self.path, self.config, self.analyze);
        self.history = [];
        if os.path.exists(os.path.join(self.profile.path, HISTORY_FILE)):
            with open(os.path.join(self.profile.path, HISTORY_FILE), "r") as file:
                self.history = json.load(file)
        layout = QVBoxLayout();
        layout.addWidget(self.tabs);
        self.tab_page_browser.setLayout(layout);
        self.setStyleSheet(self.load_styles())
        self.init_shortcuts()
        if os.path.exists( os.path.join(os.environ["USER_BROWSER_PATH"], "tabs.json" ) ):
            with open( os.path.join(os.environ["USER_BROWSER_PATH"], "tabs.json" ), "r") as f:
                js_data = json.loads( f.read() );
                for i in range(len(js_data["tab"])):
                    self.new_tab(url=js_data["tab"][i]["url"]);
        if self.tabs.count() == 0:
            self.new_tab(url=self.config["default"]["url"]);
    def closeEvent(self, event):
        js_data = {"tab" : []};
        for i in range(self.tabs.count()):
            js_data["tab"].append( { "active" : False, "url" : self.tabs.widget(i).url_bar.text() } );
        with open( os.path.join(os.environ["USER_BROWSER_PATH"], "tabs.json" ), "w") as f:
            f.write( json.dumps( js_data, ensure_ascii=False ) );
        super().closeEvent(event);

    def save(self):
        #if os.path.exists(os.path.join(self.profile.path, HISTORY_FILE)):
        with open(os.path.join(self.profile.path, HISTORY_FILE), "w") as file:
            file.write( json.dumps( self.history ) );
    
    def the_button_was_clicked(self):
        QApplication.quit();
        exit(0);
    
    def new_tab_event(self):
        return self.new_tab(None);
    
    def new_tab(self, url=None):
        if url != None and type(url) != type(""):
            url = url.toString();
        if url == None:
            clipboard = QApplication.clipboard()
            mimeData = clipboard.mimeData()
            if mimeData.hasText() and is_valid_url(mimeData.text()):
                url = mimeData.text();
            else:
                url = self.config["default"]["url"];
        tab = BrowserTab(self, url=url)
        index = self.tabs.addTab(tab, "New Tab")
        self.tabs.setCurrentIndex(index)
        tab.url_bar.setFocus();
    
    def minimize(self):
        self.showMinimized();
    
    def close_application(self):
        self.close();
        sys.exit(0);

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index);
    
    def load_styles(self):
        return open( os.path.join( BROWSER_PATH, "browser", "resources", "style.txt" ), "r" ).read();
    
    def init_shortcuts(self):
        close_action = QAction(self)
        close_action.setShortcut("Ctrl+Q")
        close_action.triggered.connect(self.close_application)
        self.addAction(close_action)

        new_tab_action = QAction(self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(self.new_tab_event)
        self.addAction(new_tab_action)

        #history_action = QAction(self)
        #history_action.setShortcut("Ctrl+H")
        #history_action.triggered.connect(self.show_history)
        #self.addAction(history_action)

        close_tab_action = QAction(self)
        close_tab_action.setShortcut("Ctrl+W")
        close_tab_action.triggered.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        self.addAction(close_tab_action)

        close_tab_action = QAction(self)
        close_tab_action.setShortcut("Ctrl+N")
        close_tab_action.triggered.connect(self.minimize)
        self.addAction(close_tab_action)
        
