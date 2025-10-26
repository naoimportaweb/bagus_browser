import sys, uuid, json, os, traceback

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QWidget, QTabWidget, QPushButton, QMessageBox
from PySide6.QtCore import Qt

from browser.ui.table import *
from browser.form_navigation_script import FormNavigationScript;

class PanelNavigation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent);
        self.parent_ = parent;
        self.tab_navigation = QTabWidget();
        self.tab_navigation.setTabsClosable(False);
        self.tab_navigation.setDocumentMode(True);
        self.tab_navigation_scripts = QWidget()
        self.tab_navigation.addTab(self.tab_navigation_scripts,    "Scripts")
        self.tab_navigation_block_tag = QWidget()
        self.tab_navigation.addTab(self.tab_navigation_block_tag, "Block TAG");
        layout = QVBoxLayout();
        layout.addWidget(self.tab_navigation);
        self.setLayout(layout);

        self.tab_navigation_scripts_table = Table.widget_tabela(self.parent_, ["name", "url", "active"], double_click=self.tab_navigation_scripts_table_click);
        self.tab_navigation_block_tag_table = Table.widget_tabela(self.parent_, ["name", "tag", "active"], double_click=self.tab_navigation_block_tag_table_click);
        layout = QVBoxLayout();
        layout.addWidget(  self.tab_navigation_scripts_table);
        self.tab_navigation_scripts.setLayout( layout );
        layout = QVBoxLayout();
        layout.addWidget(self.tab_navigation_block_tag_table);
        self.tab_navigation_block_tag.setLayout( layout );
        self.load_scripts();

    def load_scripts(self):
        dir_scripts = os.path.join( BROWSER_PATH, "browser", "resources", "scripts_block" );
        files = os.listdir( dir_scripts );
        self.tab_navigation_scripts_table.cleanList();
        for file in files:
            dir_script = os.path.join( dir_scripts, file );
            js_script = json.loads( open( dir_script, "r" ).read() );
            js_script["file_name"] = file;
            if js_script["active"] :
                js_script["active_text"] = "Active (running)";
            else:
                js_script["active_text"] = "Inactive";
            self.tab_navigation_scripts_table.add( [ js_script["name"], js_script["url"], js_script["active_text"] ], js_script ); 
    def tab_navigation_scripts_table_click(self):
        f = FormNavigationScript(self.tab_navigation_scripts_table.lista[self.tab_navigation_scripts_table.currentRow()]);
        f.exec_();
    def tab_navigation_block_tag_table_click(self):
        pass