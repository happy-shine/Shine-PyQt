import sys

from PyQt6 import QtWidgets

from my_ui import My_Ui

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = My_Ui()
    ui.show()
    sys.exit(app.exec())
