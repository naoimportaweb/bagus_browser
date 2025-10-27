import os, sys, subprocess, traceback, uuid, random, shutil, json;

BROWSER_PATH = os.path.dirname(os.path.realpath(__file__));
os.environ["BROWSER_PATH"] = BROWSER_PATH;
os.environ["BROWSER_SECURE"] = "0";
os.environ["USER_BROWSER_PATH"] = "";
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-logging --log-level=3"
os.environ["BROWSER_CONFIG"] =        "config_v1";
DEBUG_PORT = '5588'
DEBUG_URL = 'http://127.0.0.1:%s' % DEBUG_PORT
os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = DEBUG_PORT

os.environ["BROSER_DIR_SETTINGS_FILE_NAME"] = "";
os.environ["BROSER_DIR_TMP"] = "";

#from PySide6.QtWebEngine import QtWebEngine
#from PySide6.QtWebEngineCore import QtWebEngine
#from PySide6.QtWebEngineQuick import QtWebEngineQuick
from PySide6.QtWidgets import QApplication
from browser.browser import Browser;
from browser.form_login import FormLogin;
from browser.form_generic import FormGeneric;
from browser.api.proxy_helper import ProxyHelper;

def main():
    #QtWebEngineQuick.initialize(); # descobri que nao é necessário
    app = QApplication(sys.argv)
    f = FormLogin();
    f.exec();
    
    if f.diretorio == None:
        f.diretorio = os.path.expanduser("~/bagus");
        if not os.path.exists(f.diretorio):
            os.makedirs(f.diretorio);
    path_file_config = os.path.join( f.diretorio, "config.json" );
    if not os.path.exists(path_file_config):
        shutil.copy2( os.path.join(BROWSER_PATH,"data", "template.json"),  path_file_config );

    os.environ["BROSER_DIR_SETTINGS_FILE_NAME"] = os.path.join( os.environ["USER_BROWSER_PATH"], os.environ["BROWSER_CONFIG"], "settings.selected.json" );
    os.environ["BROSER_DIR_TMP"] = os.path.join( os.environ["USER_BROWSER_PATH"], "tmp");
    if os.path.exists(os.environ["BROSER_DIR_SETTINGS_FILE_NAME"]):
        proxy_js = json.loads( open(os.environ["BROSER_DIR_SETTINGS_FILE_NAME"], "r" ).read() );
        ph = ProxyHelper();
        ph.set_proxy( proxy_js["proxy"] );
    browser = Browser(f.diretorio)
    browser.show()
    sys.exit(app.exec());

if __name__ == "__main__":
    if os.name != 'nt':
        main();
    else:
        print("Só em um Sistema Operacional de Verdade!!!");

