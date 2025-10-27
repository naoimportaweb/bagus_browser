import tldextract, sys, uuid, json, os, importlib, traceback

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QGridLayout, QTextEdit, QWidget, QTabWidget, QPushButton, QMessageBox, QTabWidget
from PySide6.QtCore import Qt

from browser.ui.table import *
from browser.panel_myass_workflow import PanelMyassWorkflow;
from browser.api.myass_helper import *
from browser.ui.data_widget import DataWidget;

class PanelMyass(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent);
        self.parent_ = parent;
        self.tab_myass = QTabWidget();
        self.tab_myass.setTabsClosable(False);
        self.tab_myass.setDocumentMode(True);
        self.tab_myass_works = QWidget()
        self.tab_myass.addTab(self.tab_myass_works,    "Tasks")
        self.tab_myass_workflow = PanelMyassWorkflow(self.parent_)
        self.tab_myass.addTab(self.tab_myass_workflow, "Workflow");
        self.DIR_MYASS_TEMPLATE = os.path.join( os.environ["BROWSER_PATH"], "browser", "resources", "template", "myass.json" );
        self.tab_myass_settings = DataWidget( json.loads( open(self.DIR_MYASS_TEMPLATE, "r").read() ) );
        self.tab_myass.addTab(self.tab_myass_settings, "Settings");
        layout = QVBoxLayout();
        layout.addWidget(self.tab_myass);
        self.setLayout(layout);
        #--------------------------- works --------------
        self.table = Table.widget_tabela(self.parent_, ["result", "step", "workflow"], double_click=self.table_double_click); #, 
        layout = QVBoxLayout();
        layout.addWidget(self.table);
        btn_atualizar = QPushButton("Atualizar");
        layout.addWidget(btn_atualizar);
        btn_atualizar.clicked.connect(self.btn_atualizar_click);
        self.tab_myass_works.setLayout(layout);
        self.btn_atualizar_click();
        
    def table_double_click(self, item):
        work = self.table.lista[self.table.currentRow()];
        if len(json.loads(work["result"]).keys()) > 0:
            f = FormWork(work);
            f.exec_();
        else:
            print(work);
        pass;
    
    def _loadFinished(self):
        self.page.toPlainText(self.callable_text);
    
    def callable_text(self, data):
        self.html = data;
        js = json.loads( data );
        data = self.page.decrypt_array( js["data"], ["data", "result", "step", "workflow", "input"] );
        self.atualizar_grid( data );

    def btn_atualizar_click(self):
        self.page = MyassHelper(parent=self.parent_);
        self.page.loadFinished.connect(self._loadFinished);
        self.page.post("service/works_list.php", {  });

    def atualizar_grid(self, trabalhos):
        trabalhos = self.formata_trabalhos(trabalhos);
        self.table.cleanList();
        for i in range(len(trabalhos)):
            self.table.add([trabalhos[i]["result"], trabalhos[i]["step"], trabalhos[i]["workflow"]], trabalhos[i]);
    
    def formata_trabalhos(self, trabalhos):
        retorno = [];
        for trabalho in trabalhos:
            workflow = trabalho["workflow"];
            if workflow == None:
                workflow = "";
            step = trabalho.get("step");
            if step == None:
                step = "";
            result = trabalho["result"];
            if result == None:
                result = "";
            work = trabalho["data"];
            if work == None:
                work = "";
            input_ = trabalho.get("input");
            if input_ == None:
                input_ = "";
            retorno.append({"workflow" : workflow, "step" : step, "result" : result, "work" : work, "input" : input_});
        return retorno;

class FormWork(QDialog):
    def __init__(self, work):
        super().__init__();
        self.resize(600, 320);
        self.work = work;
        print(work);
        layout = QGridLayout();
        layout.setContentsMargins(20, 20, 20, 20);
        layout.setSpacing(10);
        path_config = os.path.expanduser( "~/bagus/myass.json" );
        config = json.loads( open( path_config, "r" ).read() );
        workflow = None;
        self.setStyleSheet(self.load_styles());
        for buffer in config["workflow"]: # deveria usar lambda, mas estou com saconcheio, trabalhei a semana toda.
            if buffer["name"] == work["workflow"]:
                workflow = buffer;
                break;
        if workflow == None: # estou desatualizado!!!!
            self.textEdit = QTextEdit();
            text = work["workflow"] + "\n----------\n" + work["work"] + "\n----------\n" + work["result"];
            self.textEdit.setPlainText( text );
            layout.addWidget(self.textEdit, 3, 0, 1, 3)
            self.setLayout(layout)
        else:
            layout_campos = QVBoxLayout();
            form_output = workflow["form"]["output"];
            if form_output != None:
                for element in form_output["elements"]:
                    self.criar_layout(layout_campos, element);
            self.setLayout(layout_campos)
    def criar_layout(self, layout_root, element):
        for child in element["elements"]:
            if child["type"] == "text" or child["type"] == "url":
                input_element = QTextEdit();
                layout_root.addWidget(input_element);
                if child.get("data") != None:
                    texto_buffer = json.loads(self.work["result"])[   child["data"]["field"]    ];
                    input_element.setPlainText( texto_buffer.strip() );
            elif child["type"] == "varchar":
                input_element = QLineEdit();
                layout_root.addWidget(input_element);
            elif child["type"] == "panel":
                layout = QVBoxLayout();
                widget1 = QWidget();
                widget1.setLayout( layout );
                layout_root.addWidget(widget1);
                self.criar_layout(layout, child);
    def load_styles(self):
        return open( os.path.join( BROWSER_PATH, "browser", "resources", "style.txt" ), "r" ).read();