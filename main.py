import os
import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog,  QCompleter, QLineEdit, QLabel
from PySide6.QtCore import QStringListModel, Qt
import re


class Document:
    def __init__(self, path, has_headers):
        self.headers, self.body = self.load(path, has_headers)    
    
    def load(self, path: str, has_headers: bool):
        lines = []
        headers = []
        body = []
        if os.path.exists(path):
            with open(path) as f:
                lines = f.readlines()
                
                headers = list(range(0, len(lines[0].split(','))))
                if has_headers:    
                    headers = lines[0].split(',')
                    body = lines[1:]
            return headers, body    
        return 0, body

class DistributionList(Document):
    
    def __init__(self, path, has_headers):
        super().__init__(path, has_headers)

class LoadDistributionListButton(QPushButton):
    def __init__(self, parent, label):
        super().__init__(label)
        self.parent = parent
        self.clicked.connect(self.handleClick)
    def handleClick(self):
        file_path, _ = QFileDialog.getOpenFileName(self.parent, "Select the distribution list")
        self.parent.distributionList = DistributionList(file_path, True)
        self.parent.model.setStringList(self.parent.distributionList.headers)
        
class FieldCompleter(QCompleter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def pathFromIndex(self, index):
        path = super().pathFromIndex(index)
        currentText = self.completionPrefix()
        if currentText[-1].strip():
            prefix = ' '.join(currentText.split(' ')[:-1])
            return prefix + " {{" + path.strip() + "}}"
        return currentText + "{{" + path.strip() + "}}" 
    
    def splitPath(self, path):
        words = re.split(r'\s+', path)
        if words:
            return [words[-1]]
        return [""]

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.documents = []

        self.label = QLabel("To:")
        

        self.line_edit = QLineEdit()
        
        self.model = QStringListModel([])
        self.completer = FieldCompleter()
        self.completer.setModel(self.model)
        self.completer.setFilterMode(Qt.MatchContains)

        self.line_edit.setCompleter(self.completer)

        self.setWindowTitle("Email Burst")
        self.resize(300, 200)
        
        self.load_dist_list_btn = LoadDistributionListButton(self ,"Load Distribution List")
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.load_dist_list_btn)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line_edit)



def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__== "__main__":
    main()