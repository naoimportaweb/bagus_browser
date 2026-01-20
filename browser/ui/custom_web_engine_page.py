import tldextract, sys, uuid, json, os, importlib, traceback, hashlib;
import threading, re;

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from datetime import datetime;
from PySide6.QtWidgets import QLayout, QDialog, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtWebEngineCore import QWebEnginePage
from browser.api.logger_helper import *

def get_file_extension_os(url):
    url = url[url.rfind("/") + 1:];
    _, file_extension = os.path.splitext(url);
    if file_extension.find("?") > 0:
        return file_extension.split("?")[0].strip();
    return file_extension.strip();

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent):
        super().__init__(profile, parent);
        self.download_ext = [".iso", ".zip", ".gz", ".png", ".jpg", ".json"];
        self.certificateError.connect( self.certificateError_signal );
        self.urlChanged.connect(self.urlChanged_signal);
        self.loadStarted.connect(self.loadStarted_signal);
        self.navigationRequested.connect(self.navigationRequested_signal); 
        self.logger_javascript = setup_logger( "javascript", os.path.join( os.environ["USER_BROWSER_PATH"], "log", "javascript.log"));
    def loadStarted_signal(self):
        pass;
    def navigationRequested_signal(self, request):
        print(request.isMainFrame(), request.navigationType(), request.url().toString()[:50]);
        request.accept();
    def newWindowRequested(self, request):
        pass;
    def urlChanged_signal(self, url):
        pass;
    def on_navigate_signal(self):
        pass;
    def certificateError_signal(self, qwebenginecertificateerror):
        pass;
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        self.logger_javascript.info( "("+ str(level) +") - " + message + " => " + sourceId + "("+ str(lineNumber) +")" );
        pass;
    
    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        if os.path.exists(os.environ["BROSER_DIR_SETTINGS_FILE_NAME"]):
            config_settings = json.loads( open(os.environ["BROSER_DIR_SETTINGS_FILE_NAME"], "r" ).read() );
            if config_settings.get("download_extension") != None:
                regex_expressions = config_settings.get("download_extension").split(" ");
                for regex_expression in regex_expressions:
                    if regex_expression.strip() == "":
                        continue;
                    regexp = re.compile(regex_expression)
                    if regexp.search(url.toString()):
                        DIR_DOWNLOAD = os.path.join( os.environ["USER_BROWSER_PATH"], "download");
                        download_js = {"url" : url.toString(), "proxy" : True, "clamscan" : True, "directory" : None, "hash" : hashlib.md5( url.toString().encode() ).hexdigest(), "filename" : url.toString()[ url.toString().rfind("/") + 1: ], "date" :  f'{datetime.now():%Y-%m-%d %H:%M:%S%z}' };
                        if not os.path.exists( os.path.join(DIR_DOWNLOAD, download_js["hash"] + ".json") ):
                            with open(os.path.join(DIR_DOWNLOAD, download_js["hash"] + ".json"), "w") as f:
                                f.write( json.dumps( download_js, ensure_ascii=False ) );
                            break;
        return super().acceptNavigationRequest(url, _type, isMainFrame);
        
