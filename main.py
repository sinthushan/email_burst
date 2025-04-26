import os
import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QComboBox

class Document:
    def __init__(self, path, has_headers):
        self.headers, self.body = self.load(path, has_headers)    
    
    def load(self, path: str, has_headers: bool):
        lines = []
        headers = []
        if os.path.exists(path):
            with open(path) as f:
                lines = f.readlines()
                
                headers = list(range(0, len(lines[0].split(','))))
                if has_headers:    
                    headers = lines[0].split(',')
            return headers, lines    
        return 0, lines

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
        self.parent.distributionList = DistributionList(file_path, False)
        self.parent.combo.addItems(map(str, self.parent.distributionList.headers))

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.documents = []

        self.combo = QComboBox()
        self.setWindowTitle("Email Burst")
        self.resize(300, 200)
        
        self.load_dist_list_btn = LoadDistributionListButton(self ,"Load Distribution List")
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.load_dist_list_btn)
        self.layout.addWidget(self.combo)




def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__== "__main__":
    main()