import tldextract, sys, uuid, json, os, importlib

BROWSER_PATH = os.environ["BROWSER_PATH"]

sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QLayout, QDialog, QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QTabWidget, QListWidget, QPushButton, QButtonGroup, QToolBar
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings, QWebEngineUrlRequestInterceptor
from urllib.parse import urlparse
from adblockparser import AdblockRules
from browser.api.logger_helper import *

#pip install adblockparser1
#https://stackoverflow.com/questions/53330056/pyqt5-pyside2-adblock
class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, analyze, parent=None):
        super().__init__(parent);
        self.domains_block = open( os.path.join(os.environ["USER_BROWSER_PATH"], "ad_hosts_block.txt"), "r").read();
        self.analyze = analyze;
        logging.basicConfig(filename= os.path.join( os.environ["USER_BROWSER_PATH"], "log", "block.log"), format='%(asctime)s %(message)s',filemode='a', level=logging.INFO)
        self.logger_block = setup_logger( "block", os.path.join( os.environ["USER_BROWSER_PATH"], "log", "block.log"));
    
    def interceptRequest(self, info):
        url = info.requestUrl().toString();
        ex = tldextract.extract( url );
        if not self.analyze.allow(url):
            info.block(True);
            print("URL interceptada pela classe Analyze: ", url);
            return;
        domain = ex.subdomain + "." + ex.domain + "." + ex.suffix;
        if self.domains_block.find( domain ) >= 0:
            self.logger_block.info(url);
            info.block(True);
            print("URL interceptada por domínio bloqueado: ", url);
            return;
        info.block(False);

#https://doc.qt.io/qt-6/qtwebengine-webenginequick-quicknanobrowser-example.html
class PrivateProfile(QWebEngineProfile):
    def __init__(self, path, config, analyze, parent=None):
        super().__init__("default")
        self.path = path;
        self.analyze = analyze;
        self.intercept = WebEngineUrlRequestInterceptor(analyze);
        self.setUrlRequestInterceptor(self.intercept);
        self.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies);
        self.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
        self.setPersistentPermissionsPolicy(QWebEngineProfile.PersistentPermissionsPolicy.StoreOnDisk);
        self.setPersistentStoragePath( os.path.join( self.path, "default" ) )
        self.setCachePath( os.path.join( self.path, "default" ) );
        #self.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36");
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled,               config["settings"]["LocalStorageEnabled"]); 
        settings.setAttribute(QWebEngineSettings.XSSAuditingEnabled,                config["settings"]["XSSAuditingEnabled"]);
        settings.setAttribute(QWebEngineSettings.HyperlinkAuditingEnabled,          config["settings"]["HyperlinkAuditingEnabled"]);
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled,          config["settings"]["FullScreenSupportEnabled"]);
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard,      config["settings"]["JavascriptCanAccessClipboard"]);
        settings.setAttribute(QWebEngineSettings.PluginsEnabled,                    config["settings"]["PluginsEnabled"]);
        settings.setAttribute(QWebEngineSettings.AutoLoadImages,                    config["settings"]["AutoLoadImages"]);
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled,                 config["settings"]["JavascriptEnabled"]);
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows,          config["settings"]["JavascriptCanOpenWindows"]);
        settings.setAttribute(QWebEngineSettings.LinksIncludedInFocusChain,         config["settings"]["LinksIncludedInFocusChain"]);
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls,   config["settings"]["LocalContentCanAccessRemoteUrls"]);
        settings.setAttribute(QWebEngineSettings.XSSAuditingEnabled,                config["settings"]["XSSAuditingEnabled"]);
        settings.setAttribute(QWebEngineSettings.SpatialNavigationEnabled,          config["settings"]["SpatialNavigationEnabled"]);
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls,     config["settings"]["LocalContentCanAccessFileUrls"]);
        settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled,             config["settings"]["ScrollAnimatorEnabled"]);
        settings.setAttribute(QWebEngineSettings.ErrorPageEnabled,                  config["settings"]["ErrorPageEnabled"]);
        settings.setAttribute(QWebEngineSettings.ScreenCaptureEnabled,              config["settings"]["ScreenCaptureEnabled"]);
        settings.setAttribute(QWebEngineSettings.WebGLEnabled,                      config["settings"]["WebGLEnabled"]);
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled,        config["settings"]["Accelerated2dCanvasEnabled"]);
        settings.setAttribute(QWebEngineSettings.AutoLoadIconsForPage,              config["settings"]["AutoLoadIconsForPage"]);
        settings.setAttribute(QWebEngineSettings.TouchIconsEnabled,                 config["settings"]["TouchIconsEnabled"]);
        settings.setAttribute(QWebEngineSettings.FocusOnNavigationEnabled,          config["settings"]["FocusOnNavigationEnabled"]);
        settings.setAttribute(QWebEngineSettings.PrintElementBackgrounds,           config["settings"]["PrintElementBackgrounds"]);
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent,       config["settings"]["AllowRunningInsecureContent"]);
        settings.setAttribute(QWebEngineSettings.AllowGeolocationOnInsecureOrigins, config["settings"]["AllowGeolocationOnInsecureOrigins"]);
        settings.setAttribute(QWebEngineSettings.AllowWindowActivationFromJavaScript,config["settings"]["AllowWindowActivationFromJavaScript"]);
        settings.setAttribute(QWebEngineSettings.ShowScrollBars,                    config["settings"]["ShowScrollBars"]);
        settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture,       config["settings"]["PlaybackRequiresUserGesture"]);
        settings.setAttribute(QWebEngineSettings.JavascriptCanPaste,                config["settings"]["JavascriptCanPaste"]);
        settings.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly,        config["settings"]["WebRTCPublicInterfacesOnly"]);
        settings.setAttribute(QWebEngineSettings.DnsPrefetchEnabled,                config["settings"]["DnsPrefetchEnabled"]);
        settings.setAttribute(QWebEngineSettings.PdfViewerEnabled,                  config["settings"]["PdfViewerEnabled"]);
        settings.setAttribute(QWebEngineSettings.NavigateOnDropEnabled,             config["settings"]["NavigateOnDropEnabled"]);
        settings.setAttribute(QWebEngineSettings.ReadingFromCanvasEnabled,          config["settings"]["ReadingFromCanvasEnabled"]);
        settings.setAttribute(QWebEngineSettings.ForceDarkMode,                     config["settings"]["ForceDarkMode"]);
        settings.setAttribute(QWebEngineSettings.PrintHeaderAndFooter,              config["settings"]["PrintHeaderAndFooter"]);
        settings.setAttribute(QWebEngineSettings.PreferCSSMarginsForPrinting,       config["settings"]["PreferCSSMarginsForPrinting"]);
        settings.setAttribute(QWebEngineSettings.TouchEventsApiEnabled,             config["settings"]["TouchEventsApiEnabled"]);
