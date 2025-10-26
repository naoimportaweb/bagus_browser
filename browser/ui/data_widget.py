import os, sys, inspect, json;

from PySide6.QtCore import (QByteArray, QFile, QFileInfo, QSettings, QSaveFile, QTextStream, Qt, Slot)
from PySide6.QtWidgets import (QWidget, QLineEdit, QMessageBox, QTextEdit, QDialog, QLabel, QGridLayout, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout)

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

class DataWidget(QWidget):
    def __init__(self, layout_js):
        super().__init__();
        self.layout_js = layout_js;
        self.layout = QVBoxLayout();
        self.setLayout(self.layout);
        self.load_data(self.layout_js["elements"]);
        self.criar_layout( self.layout, self.layout_js["elements"], None);
        self.layout.addStretch();
        self.btn_salvar = QPushButton("Save");
        #self.btn_close = QPushButton("Close");
        self.btn_salvar.clicked.connect(self.btn_salvar_click)
        self.widget_linha(self.layout, [self.btn_salvar], stretch_inicio=True, stretch_fim=False);

    def save_data(self, elements, data, database=None):
        for child in elements:
            if child["type"] == "panel":
                self.save_data(child["elements"], child["data"], database=child.get("database"));
            elif child["type"] == "varchar" or child["type"] == "secret":
                if data != None:
                    data[ child["field"] ] = child["input"].text();
            elif child["type"] == "text" or child["type"] == "url":
                if data != None:
                    data[ child["field"] ] =  child["input"].toPlainText();
        if data != None and database != None:
            if database["type"] == "json":
                with open( database["file"], "w" ) as f:
                    f.write( json.dumps( data , ensure_ascii=False) );

    def btn_salvar_click(self):
        self.save_data(self.layout_js["elements"], None);
        #self.close();
        msgBox = QMessageBox();
        msgBox.setText("Done!!!");
        msgBox.exec();

    def load_data(self, elements):
        for child in elements:
            if child["type"] == "panel":
                if child["database"]["type"] == "json":
                    if child["database"]["file"][0] == "~":
                        child["database"]["file"] = os.path.expanduser(child["database"]["file"]);
                    if os.path.exists(child["database"]["file"]):
                        child["data"] = json.loads( open( child["database"]["file"], "r" ).read() );
                    else:
                        child["data"] = {};
                self.load_data(child["elements"]);
    
    def criar_layout(self, layout_root, elements, data):
        for child in elements:
            if child["type"] == "text" or child["type"] == "url":
                input_element = QTextEdit();
                input_label = QLabel(child["label"]);
                layout_root.addWidget(input_label);
                layout_root.addWidget(input_element);
                if data != None:
                    input_element.setPlainText( data.get(child["field"]) );
                child["input"] = input_element;
            elif child["type"] == "varchar":
                input_element = QLineEdit();
                input_label = QLabel(child["label"]);
                if data != None:
                    input_element.setText( data.get(child["field"]) );
                child["input"] = input_element;
                self.widget_linha(layout_root, [input_label, input_element]);
            elif child["type"] == "secret":
                input_element = QLineEdit();
                input_label = QLabel(child["label"]);
                input_element.setEchoMode(QLineEdit.EchoMode.Password);
                if data != None:
                    input_element.setText( data.get(child["field"]) );
                child["input"] = input_element;
                self.widget_linha(layout_root, [input_label, input_element]);
            elif child["type"] == "panel":
                layout = QVBoxLayout();
                widget1 = QWidget();
                widget1.setLayout( layout );
                layout_root.addWidget(widget1);
                self.criar_layout(layout, child["elements"], child["data"]);
    def widget_linha(self, layout, controls, stretch_inicio=False, stretch_fim=False):
        widget1 = QWidget();
        widget1_layout = QHBoxLayout();
        widget1.setLayout(widget1_layout);
        if stretch_inicio:
            widget1_layout.addStretch();
        for control in controls:
            if type(control).__name__ == type("").__name__:
                widget1_layout.addStretch();
                continue;
            widget1_layout.addWidget( control );
        if stretch_fim:
            widget1_layout.addStretch();
        layout.addWidget(widget1);

