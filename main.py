import os
import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog,  QCompleter, QLineEdit, QLabel, QTextEdit
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
                    headers = self.clean_headers(headers)
                    body = lines[1:]
            return headers, body    
        return 0, body

    def clean_headers(self, headers):
        cleaned_headers = []
        for header in headers:
            cleaned_headers.append(header.replace('\n', ''))
        return cleaned_headers

class GetFilePathButton(QPushButton):
    def __init__(self, parent, label):
        super().__init__(label)
        self.parent = parent
        self.clicked.connect(self.handleClick)
    def handleClick(self):
        file_path, _ = QFileDialog.getOpenFileName(self.parent, "Select the distribution list")
        self.parent.file_path.setText(file_path)

class LoadFileButton(QPushButton):
    def __init__(self, parent, label):
        super().__init__(label)
        self.parent = parent
        self.clicked.connect(self.handleClick)
    def handleClick(self):
        name = self.parent.name.text().strip()
        if name:
            file_path = self.parent.file_path.text() 
            self.parent.documents[name] = Document(file_path, True)
            self.parent.reset_string_list()
            self.parent.name.setText('')
            self.parent.file_path.setText('')
        
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

class CompleterTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._completer = None
        
    def setCompleter(self, completer):
        if self._completer:
            self._completer.activated.disconnect()
            
        self._completer = completer
        
        if not self._completer:
            return
            
        completer.setWidget(self)
        completer.activated.connect(self.insertCompletion)
        
    def completer(self):
        return self._completer
        
    def insertCompletion(self, completion):
        if not self._completer:
            return
            
        tc = self.textCursor()
        # Get the current text up to the cursor position
        text_up_to_cursor = self.toPlainText()[:tc.position()]
        
        # Find where the current word begins
        word_start = 0
        for i in range(len(text_up_to_cursor) - 1, -1, -1):
            if i < len(text_up_to_cursor) and text_up_to_cursor[i].isspace():
                word_start = i + 1
                break
                
        # Calculate how many characters to remove
        extra = len(text_up_to_cursor) - word_start
        
        # Move cursor back to remove the current word
        for i in range(extra):
            tc.deletePreviousChar()
            
        # Insert the completion
        tc.insertText(completion)
        self.setTextCursor(tc)
        
    def textUnderCursor(self):
        tc = self.textCursor()
        text = self.toPlainText()
        position = tc.position()
        
        # Get text up to cursor
        text_up_to_cursor = text[:position]
        
        # Get the last word
        words = text_up_to_cursor.split()
        return words[-1] if words else ""
        
    def keyPressEvent(self, event):
        if self._completer and self._completer.popup().isVisible():
            # The following keys are forwarded by the completer to the widget
            if event.key() in (
                Qt.Key_Enter,
                Qt.Key_Return,
                Qt.Key_Escape,
                Qt.Key_Tab,
                Qt.Key_Backtab,
            ):
                event.ignore()
                return
                
        # Auto-complete on Ctrl+Space
        isShortcut = (event.modifiers() == Qt.ControlModifier and
                      event.key() == Qt.Key_Space)
        
        # Don't process if we're handling a shortcut
        if not self._completer or not isShortcut:
            super().keyPressEvent(event)
            
        # Show completions on shortcut or when typing
        ctrlOrShift = event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)
        if not self._completer or (ctrlOrShift and event.text() == ''):
            return
            
        eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-="  # End of word characters
        hasModifier = (event.modifiers() != Qt.NoModifier) and not ctrlOrShift
        
        # Only show completer for typing or explicit shortcut
        if not isShortcut and (hasModifier or 
                             not event.text() or 
                             len(event.text()) == 0 or 
                             event.text()[-1] in eow):
            self._completer.popup().hide()
            return
            
        # Get current text to cursor position
        completionPrefix = self.textUnderCursor()
        
        # If the user has just started typing a word, don't complete
        if len(completionPrefix) < 1 and not isShortcut:
            self._completer.popup().hide()
            return
            
        # Only update if the prefix changed
        if completionPrefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(completionPrefix)
            popup = self._completer.popup()
            popup.setCurrentIndex(
                self._completer.completionModel().index(0, 0)
            )
            
        # Calculate popup position
        cr = self.cursorRect()
        cr.setWidth(
            self._completer.popup().sizeHintForColumn(0) + 
            self._completer.popup().verticalScrollBar().sizeHint().width()
        )
        self._completer.complete(cr)  # Show popup


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.documents = {}

        self.label_name = QLabel("Document Name (Do Not Add Spaces):")
        self.name = QLineEdit()

        self.label_file_path = QLabel("File Path")
        self.file_path = QLineEdit()
        
        self.get_path_btn = GetFilePathButton(self ,"Get File")
        self.load_doc_btn = LoadFileButton(self, "Load File")
        
        self.label_to = QLabel("To:")
        self.to = QLineEdit()
        
        self.label_cc = QLabel("CC:")
        self.cc = QLineEdit()

        self.label_subject = QLabel("Subject:")
        self.subject = QLineEdit()


        self.model = QStringListModel([])
        self.completer = FieldCompleter()
        self.completer.setModel(self.model)
        self.completer.setFilterMode(Qt.MatchContains)

        self.to.setCompleter(self.completer)
        self.cc.setCompleter(self.completer)
        self.subject.setCompleter(self.completer)
        
        
        self.label_body = QLabel("Body:")
        self.body = CompleterTextEdit()
        self.body.setCompleter(self.completer)


        self.setWindowTitle("Email Burst")
        self.resize(300, 200)
        

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label_name)
        self.layout.addWidget(self.name)
        self.layout.addWidget(self.label_file_path)
        self.layout.addWidget(self.file_path)
        self.layout.addWidget(self.get_path_btn)
        self.layout.addWidget(self.load_doc_btn)
        self.layout.addWidget(self.label_to)
        self.layout.addWidget(self.to)
        self.layout.addWidget(self.label_cc)
        self.layout.addWidget(self.cc)
        self.layout.addWidget(self.label_subject)
        self.layout.addWidget(self.subject)
        self.layout.addWidget(self.label_body)
        self.layout.addWidget(self.body)

    def reset_string_list(self):
        suggestions = []
        for document in self.documents:
            headers = self.documents[document].headers
            suggestions.extend([f'{document}.{header}' for header in headers])
        self.model.setStringList(suggestions)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__== "__main__":
    main()