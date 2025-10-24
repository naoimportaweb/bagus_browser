import os, sys, subprocess, traceback, uuid, random, shutil;

BROWSER_PATH = os.path.dirname(os.path.realpath(__file__));
os.environ["BROWSER_PATH"] = BROWSER_PATH;
os.environ["BROWSER_SECURE"] = "0";
os.environ["USER_BROWSER_PATH"] = "";
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-logging --log-level=3"

#from PySide6.QtWebEngine import QtWebEngine
#from PySide6.QtWebEngineCore import QtWebEngine
#from PySide6.QtWebEngineQuick import QtWebEngineQuick
from PySide6.QtWidgets import QApplication
from browser.browser import Browser;
from browser.form_login import FormLogin;

def main():
    #QtWebEngineQuick.initialize();
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
    browser = Browser(f.diretorio)
    browser.show()
    sys.exit(app.exec());

if __name__ == "__main__":
    if os.name != 'nt':
        main();
    else:
        print("Só em um Sistema Operacional de Verdade!!!");

