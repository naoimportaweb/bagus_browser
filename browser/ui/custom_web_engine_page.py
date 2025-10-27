import tldextract, sys, uuid, json, os, importlib, traceback, hashlib;
import threading

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
        self.logger_javascript = setup_logger( "javascript", os.path.join( os.environ["USER_BROWSER_PATH"], "log", "javascript.log"));
    def loadStarted_signal(self):
        pass;
    def navigationRequested(self, request):
        print("Request", request);
        pass;
    def newWindowRequested(self, request):
        print("Request", request);
        pass;
    def urlChanged_signal(self, url):
        pass;
    def on_navigate_signal(self):
        pass;
    def certificateError_signal(self, qwebenginecertificateerror):
        pass;#<PySide6.QtWebEngineCore.QWebEngineCertificateError object at 0x7f07e0445c80>
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        #print("("+ str(level) +") - " + message + " => " + sourceId + "("+ str(lineNumber) +")");
        self.logger_javascript.info( "("+ str(level) +") - " + message + " => " + sourceId + "("+ str(lineNumber) +")" );
        pass;
    
    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        if os.path.exists(os.environ["BROSER_DIR_SETTINGS_FILE_NAME"]):
            config_settings = json.loads( open(os.environ["BROSER_DIR_SETTINGS_FILE_NAME"], "r" ).read() );
            extensao = get_file_extension_os(url.toString());
            if extensao != None and extensao != "" and config_settings["download_extension"].find(extensao) >= 0:
                localizado = False;
                DIR_DOWNLOAD = os.path.join( os.environ["USER_BROWSER_PATH"], "download");
                download_js = {"url" : url.toString(), "proxy" : True, "clamscan" : True, "directory" : None, "hash" : hashlib.md5( url.toString().encode() ).hexdigest(), "filename" : url.toString()[ url.toString().rfind("/") + 1: ], "date" :  f'{datetime.now():%Y-%m-%d %H:%M:%S%z}' };
                if not os.path.exists( os.path.join(DIR_DOWNLOAD, download_js["hash"] + ".json") ):
                    with open(os.path.join(DIR_DOWNLOAD, download_js["hash"] + ".json"), "w") as f:
                        f.write( json.dumps( download_js, ensure_ascii=False ) );
        return super().acceptNavigationRequest(url, _type, isMainFrame)
