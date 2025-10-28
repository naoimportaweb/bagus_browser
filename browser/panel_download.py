import sys, uuid, json, os, traceback, shutil, threading

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QWidget, QTabWidget, QPushButton, QMessageBox
from PySide6.QtCore import Qt, QProcess

from browser.ui.table import *

class PanelDownload(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent);
        self.parent_ = parent;
        self.table = Table.widget_tabela(self.parent_, ["URL", "File"], double_click=self.table_double_click);
        layout = QVBoxLayout();
        layout.addWidget(self.table);
        btn_atualizar = QPushButton("Atualizar");
        layout.addWidget(btn_atualizar);
        btn_atualizar.clicked.connect(self.btn_atualizar_click);
        self.setLayout(layout);
        self.load_table();
        self.in_execution = [];
    def reload_data(self):
        self.load_table();
    def load_table(self):
        DIR_DOWNLOAD = os.path.join( os.environ["USER_BROWSER_PATH"], "download");
        self.table.cleanList();
        for file in os.listdir( DIR_DOWNLOAD ):
            print(os.path.join( DIR_DOWNLOAD, file ));
            buffer_js = json.loads( open( os.path.join( DIR_DOWNLOAD, file ), "r").read() );
            self.table.add([buffer_js["url"], buffer_js["filename"]], os.path.join( DIR_DOWNLOAD, file ) );
        #lines = sorted(lines, key=lambda k: k['page'].get('update_time', 0), reverse=True)

    def download(self, url, filename, config_path):
        if url in self.in_execution:
            return;
        self.in_execution.append(url);
        os.system( 'curl -x socks5://127.0.0.1:9050 -L -O --output-dir '+ os.path.expanduser("~/Downloads") +' -k --retry 9999999999999 --retry-max-time 0 -C - ' + url );
        os.unlink( config_path );
        self.reload_data();
        #os.system( 'curl -L -O --output-dir '+ os.environ["BROSER_DIR_TMP"] +' -k --retry 9999999999999 --retry-max-time 0 -C - ' + url );
        #shutil.move( os.path.join( os.environ["BROSER_DIR_TMP"], filename ), os.path.join( os.path.expanduser("~/Downloads"), filename) );
    
    def table_double_click(self):
        buffer_js = json.loads( open(self.table.lista[ self.table.currentRow() ],"r").read() );
        x = threading.Thread(target=self.download, args=(buffer_js["url"], buffer_js["filename"], self.table.lista[ self.table.currentRow() ], ));
        x.start();
        
    def btn_atualizar_click(self):
        self.reload_data();
        pass;
    
    def clam_result_str_to_json(self, clam_result_str):
        clam_result_list = clam_result_str.split("\n")
        clam_result_list.remove('')

        results_marker = \
            clam_result_list.index("----------- SCAN SUMMARY -----------")

        hit_list = clam_result_list[:results_marker]
        summary_list = clam_result_list[(results_marker + 1):]

        r_dict = { "hits": hit_list }
        for s in summary_list:
            # in case of blank lines
            if not s:
                continue
            split_index = [c == ':' for c in s].index(True)
            k = s[:split_index].lower()
            k = k.replace(" ", "_")
            v = s[(split_index + 1):].strip(" ")
            r_dict[k] = v

        return r_dict

#p = QProcess()
#p.start("<program>", [<arguments>])