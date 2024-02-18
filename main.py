import csv
from spellchecker import SpellChecker
import os
import logging
import pandas as pd
import sys
from PyQt6.QtCore import QAbstractListModel, Qt

from PyQt6.QtWidgets import (
    QApplication, QLabel,
    QWidget, QPushButton, QListView,
    QHBoxLayout, QVBoxLayout, QGridLayout,
    QLineEdit, QFormLayout, QFileDialog,
    QDialog, QDialogButtonBox, QMessageBox,
)
from PyQt6.QtGui import (
    QIcon,
)
import pkg_resources


class SpellCheckModel(QAbstractListModel):
    def __init__(self, data=[], parent=None):
        super().__init__(parent)
        self._data = data

    def rowCount(self, parent):
        return len(self._data)

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()]


spell = SpellChecker()

folder_path = './output'
if not os.path.exists(folder_path):
    os.mkdir(folder_path)

logger = logging.getLogger()
handler_info = logging.FileHandler('./info.log')
handler_info.setLevel(logging.INFO)
handler_error = logging.FileHandler('./error.log')
handler_error.setLevel(logging.ERROR)

logger.addHandler(handler_info)
logger.addHandler(handler_error)

def rb(word):
    if word.startswith("("):
        if word.endswith(")"):
            return word[1:-1]
        return word[1:]
    elif word.endswith(")"):
        return word[:-1]
    else:
        return word

def spell_correction(word):
    if word.isupper() :
        return word
    elif word.lower() in spell.unknown([word]):
        w = spell.correction(word)
        if w and w != "i":
            return w.capitalize()
    # print (word)
    return word

def spell_check_word(word):
    if word.startswith("("):
        if word.endswith(")"):
            return "(" + spell_correction(word[1:-1]) + ")"
        return "(" + spell_correction(word[1:])
    elif word == "w/":
        return ""
    elif word.endswith(")"):
        return spell_correction(word[:-1]) + ")"
    elif word.endswith(","):
        return spell_correction(word[:-1]) + ","
    elif word.startswith("#"):
        return "#" + spell_correction(word[1:])
    elif word.endswith(":"):
        return spell_correction(word[:-1]) + ":"
    elif len(word) > 2 and word[1] == "-":
        if word[-2] != "-":
            return word[0:2] + spell_correction(word[2:])
    elif "/" in word:
        # print(word)
        # print("/".join([spell_correction(x) for x in word.split("/")]))
        return "/".join([spell_correction(x) for x in word.split("/")])
    return spell_correction(word)

def spell_check(text):
    # print(text)
    # if len(text) == 0:
        # print("error")
    # words = [rb(word) for word in text.split()]
    words = text.split()
    # print(words)
    
    # misspelled = spell.unknown(words)
    # print(misspelled)

    corrected_text = []
    for word in words:
        w = spell_check_word(word)
        if len(w) == 0:
            continue
        corrected_text.append(w)

    return ' '.join(corrected_text)

class Window(QDialog):
    def __init__(self):
        super().__init__(parent=None)
        ico_path = pkg_resources.resource_filename(__name__, '2.ico')
        self.setWindowIcon(QIcon(ico_path))
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.setWindowTitle("Spell Checker")
        dialogLayout = QVBoxLayout()
        # formLayout
        formLayout = QFormLayout()
        # layout1
        layout1 = QHBoxLayout()
        
        label1 = QLabel("Input:")
        label1.setFixedWidth(50)
        lineEdit1 = QLineEdit()
        setattr(self, "lineEdit1", lineEdit1)
        button1 = QPushButton("Open")
        button1.clicked.connect(self.on_button_click)
        
        layout1.addWidget(label1)
        layout1.addWidget(lineEdit1)
        layout1.addWidget(button1)
        # layout2
        layout2 = QHBoxLayout()
        
        label2 = QLabel("Output:")
        label2.setFixedWidth(50)
        lineEdit2 = QLineEdit()
        # lineEdit2.setFixedWidth(300)
        lineEdit2.setText(os.getcwd() + '\\output\\')
        setattr(self, "lineEdit2", lineEdit2)
        button2 = QPushButton("Select")
        button2.clicked.connect(self.on_button_click)
        
        layout2.addWidget(label2)
        layout2.addWidget(lineEdit2)
        layout2.addWidget(button2)
        # layout3
        layout3 = QHBoxLayout()
        self.listView = QListView()
        self.model = SpellCheckModel(["..."])
        self.listView.setModel(self.model)
        
        layout3.addWidget(self.listView)

        # layout4
        layout4 = QHBoxLayout()
        label = QLabel()
        label.setText("0%")
        layout4.addWidget(label)
        setattr(self, "label", label)

        buttons = QDialogButtonBox()
        buttons.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Ok
        )
        # dialogLayout.addWidget(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout4.addWidget(buttons)

        setattr(self, "buttons", buttons)

        # add layouts
        formLayout.addRow(layout1)
        formLayout.addRow(layout2)
        formLayout.addRow(layout3)
        formLayout.addRow(layout4)

        dialogLayout.addLayout(formLayout)

        self.setLayout(dialogLayout)

        msgDone = QMessageBox()
        msgDone.setWindowTitle("Alert")
        setattr(self, "messageDone", msgDone)
    def accept(self):
        fileName = self.lineEdit1.text()
        if fileName.endswith('.csv'):
            print(fileName)  
            # self.buttons.accepted.setText("...")
            # # files = [f for f in os.listdir("./input") if os.path.isfile(os.path.join("./input", f))]
            # # for file in files:
            # #     if file.endswith(".csv"):
            # print(file)
            try : 
                df = pd.read_csv(fileName)
                print(df)
                num = 0
                suggestions = []
                for i in range(0, len(df)) :
                    val = str(df.loc[i, "value"])
                    self.label.setText(f"{(i/len(df))*100:.2f}%")
                    # print(str(i) + " :  " + val)
                    val1 = spell_check(val)
                    
                    if val.replace(" ", "") == val1.replace(" ", "") :
                        # print(val + " : " + val1)
                        continue
                    else:
                        # print(f"{str(i)} : {val} : {val1}")
                        num = num + 1
                        logger.error(f"{str(i)} : {val} : {val1}")
                        
                        df.loc[i, 'Suggestion'] = val1

                        suggestions.append(f">> {i+1} : {val} : {val1}")
                        QApplication.processEvents()
                        self.model = SpellCheckModel(suggestions)
                        self.listView.setModel(self.model)
                        self.listView.scrollToBottom() 
                
                self.label.setText(f"Correct {num} values")    
                                
                df.to_csv(self.lineEdit2.text()+"output.csv", index = False)
                self.messageDone.setIcon(QMessageBox.Icon.Information)
                self.messageDone.setText(f"Corrected {num} values. \n please check info.txt file for more details.")
                self.messageDone.exec()
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                self.messageDone.setIcon(QMessageBox.Icon.Critical)
                self.messageDone.setText(f"error {e}")
                self.messageDone.exec()
        else :
            print('you can only select .csv file')
    def on_button_click(self):
        button = self.sender()
        if button.text() == "Open":
            fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Packages(*.csv)")
            # self.lineEdit1.setText(fileName.replace('/','\\'))               
            self.lineEdit1.setText(fileName)               
        elif button.text() == "Select":
            folderName = QFileDialog.getExistingDirectory(self, "Select Directory")
            self.lineEdit2.setText(folderName.replace('/','\\'))
        else :
            print('on_button_click unknown error')


if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    sys.exit(app.exec())
        # with open("./input/" + file, 'r') as f:
        #     csv_reader = csv.reader(f)
        #     # Iterate over each row in the CSV file
        #     for row in csv_reader:
        #         for col in row:
        #             print(col)
        #             col1 = spell_check(col)
        #             if col == col1:
        #                 continue
        #             else:
        #                 print(col1 )
# Specify the path to your large CSV file
# csv_file_path = 'LOV_Value_File_2-15-2024.csv'
# chunk_size = 10000  # Adjust the chunk size as needed
# chunks = []
# i = 0
# for chunk in pd.read_csv(csv_file_path, chunksize=chunk_size):
#     print(i)
#     i = i + 1
#     chunks.append(chunk)

# # Concatenate the chunks into a single DataFrame
# # df = pd.concat(chunks, ignore_index=True)
# # Open the CSV file in read mode
# with open('data.csv', mode='r') as file:
#     csv_reader = csv.reader(file)
#     # Iterate over each row in the CSV file
#     for row in csv_reader:

#         print (row)
#         for col in row:
#             col1 = spell_check(col)
#             if col == col1:
#                 continue
#             else:
#                 print(col1)

# data = [
#     ['Name', 'Age', 'City'],
#     ['Alice', 30, 'New York'],
#     ['Bob', 25, 'San Francisco'],
#     ['Charlie', 35, 'Chicago']
# ]

# # Specify the file name
# csv_file = 'data.csv'

# # Open the CSV file in write mode
# with open(csv_file, 'w', newline='') as file:
#     writer = csv.writer(file)

#     # Write data to the CSV file row by row
#     for row in data:
#         writer.writerow(row)

# print(f'Data has been written to {csv_file}')

# text = "Thiss is a samplee text withh somee misspellings."
# corrected_text = spell_check(text)
# print("Original text:", text)
# print("Corrected text:", corrected_text)