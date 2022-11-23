import os
from pathlib import Path

import cv2
import numpy as np
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QFileDialog, QToolBar, QMessageBox, QInputDialog

from automake_ui import Ui_MainWindow


class My_Ui(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.camera_model = 0
        self.timer_camera = QtCore.QTimer()
        self.cap = cv2.VideoCapture()
        self.CAM_NUM = 0
        self.toolBar = None
        self.img_pix = None
        self.img_path = ''
        self.image = QImage(self.img_path)
        self.is_cn = True
        self.init_ui()

    def init_ui(self):
        self.setupUi(self)
        self.set_toolbar()
        self.set_slider()
        self.update_image()
        self.set_slot()

    def set_slot(self):
        self.action_O.triggered.connect(self.get_image_path)
        self.gray_button.clicked.connect(self.image_gray)
        self.filter_slider.sliderReleased.connect(self.image_filter)
        self.binarization_slider.sliderReleased.connect(self.image_binarization)
        self.gammar_slider.sliderReleased.connect(self.image_gammar)
        self.edge_slider.sliderReleased.connect(self.image_edge)
        self.reset_button.clicked.connect(self.image_reset)
        self.action_Z.triggered.connect(self.image_reset)
        self.action_L.triggered.connect(self.window_translate)
        self.action_S.triggered.connect(self.save_image)
        self.action_A.triggered.connect(self.save_as_image)
        self.action_T.triggered.connect(self.color_dock.show)
        self.action_Q.triggered.connect(lambda: QCoreApplication.exit(0))
        self.action_B.triggered.connect(self.about_message)
        self.action_V.triggered.connect(self.open_camera)
        self.action_left.triggered.connect(lambda: self.set_image_index(True))
        self.action_right.triggered.connect(lambda: self.set_image_index(False))
        self.timer_camera.timeout.connect(lambda: self.show_camera())

    def set_slider(self):
        self.gammar_slider.setMinimum(0)
        self.gammar_slider.setMaximum(100)
        self.gammar_slider.setPageStep(1)
        self.gammar_slider.setValue(50)

        self.binarization_slider.setMinimum(0)
        self.binarization_slider.setMaximum(255)
        self.binarization_slider.setPageStep(1)
        self.binarization_slider.setValue(0)

        self.filter_slider.setMinimum(1)
        self.filter_slider.setMaximum(20)
        self.filter_slider.setPageStep(1)
        self.filter_slider.setValue(1)

        self.edge_slider.setMinimum(0)
        self.edge_slider.setMaximum(100)
        self.edge_slider.setPageStep(1)
        self.edge_slider.setValue(0)

    def get_image_path(self):
        home_dir = str(Path.home())
        self.fname_list = QFileDialog.getOpenFileNames(
            self,
            'Open file',
            home_dir,
            "Image Files (*.png *.jpg *.bmp *.jpeg)"
        )
        if self.fname_list[0]:
            print(self.fname_list[0].__len__())
            self.fname_index = 0
            self.img_path = self.fname_list[0][self.fname_index]
            self.image = QImage(self.img_path)
            self.update_image()

    def set_image_index(self, isLeft):
        if self.fname_list[0]:
            if isLeft:
                if self.fname_index > 0:
                    self.fname_index -= 1
            else:
                if self.fname_index < self.fname_list[0].__len__() - 1:
                    self.fname_index += 1
            self.img_path = self.fname_list[0][self.fname_index]
            self.image = QImage(self.img_path)
            self.update_image()

    def update_image(self):
        self.img_pix = QPixmap(self.image)
        self.img_pix = self.img_pix.scaled(
            self.img_label.width(),
            self.img_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio
        )
        self.img_label.setPixmap(self.img_pix)

    def resizeEvent(self, event):
        self.update_image()

    def image_gray(self):
        if self.img_path:
            img = cv2.imread(self.img_path, 1)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.image = QtGui.QImage(
                gray.data,
                gray.shape[1],
                gray.shape[0],
                QtGui.QImage.Format.Format_Grayscale8
            )
            self.update_image()

    def image_filter(self):
        if self.img_path:
            img = cv2.imread(self.img_path)
            src = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            n = self.filter_slider.value()
            blur = cv2.blur(src, (n, n))
            self.image = QtGui.QImage(
                blur.data,
                blur.shape[1],
                blur.shape[0],
                QtGui.QImage.Format.Format_RGB888
            )
            self.update_image()

    def image_binarization(self):
        if self.img_path:
            img = cv2.imread(self.img_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, binary = cv2.threshold(
                gray,
                self.binarization_slider.value(),
                255,
                cv2.THRESH_BINARY
            )
            self.image = QtGui.QImage(
                binary.data,
                binary.shape[1],
                binary.shape[0],
                QtGui.QImage.Format.Format_Grayscale8
            )
            self.update_image()

    def image_gammar(self):
        if self.img_path:
            img = cv2.imread(self.img_path)
            slider_value = self.gammar_slider.value()
            if slider_value <= 50:
                gamma = 1 - ((50 - slider_value) * 0.02)
            else:
                gamma = 1 + 0.2 * slider_value

            gamma_table = [np.power(x / 255.0, gamma) * 255.0 for x in range(256)]  # 建立映射表
            gamma_table = np.round(np.array(gamma_table)).astype(np.uint8)
            gamma_image = cv2.LUT(img, gamma_table)
            self.image = QtGui.QImage(
                gamma_image.data,
                gamma_image.shape[1],
                gamma_image.shape[0],
                QtGui.QImage.Format.Format_BGR888
            )
            self.update_image()

    def image_edge(self):
        if self.img_path:
            img = cv2.imread(self.img_path, 0)
            edge = cv2.Canny(img, 100, self.edge_slider.value() * 8)
            self.image = QtGui.QImage(
                edge.data,
                edge.shape[1],
                edge.shape[0],
                QtGui.QImage.Format.Format_Grayscale8
            )
            self.update_image()

    def image_reset(self):
        self.image = QImage(self.img_path)
        self.update_image()
        self.set_slider()

    def window_translate(self):
        self.is_cn = not self.is_cn
        if self.is_cn:
            self.retranslateUi(self)
        else:
            self.retranslateUi_en(self)

    def retranslateUi_en(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "简易图像处理  ver. 1.0 from Shine 209050926"))
        self.menu_F.setTitle(_translate("MainWindow", "File(&F)"))
        self.menu_E.setTitle(_translate("MainWindow", "Edit(&E)"))
        self.menu_W.setTitle(_translate("MainWindow", "Window(&W)"))
        self.menu_H.setTitle(_translate("MainWindow", "Help(&H)"))
        self.color_dock.setWindowTitle(_translate("MainWindow", "Color transform"))
        self.gammar_label.setText(_translate("MainWindow", "Gamma"))
        self.gray_button.setText(_translate("MainWindow", "Gray"))
        self.binarization_label.setText(_translate("MainWindow", "Binarization"))
        self.filter_label.setText(_translate("MainWindow", "Filter"))
        self.edge_label.setText(_translate("MainWindow", "Edge"))
        self.reset_button.setText(_translate("MainWindow", "Reset"))
        self.action_O.setText(_translate("MainWindow", "Open image(&O)"))
        self.action_S.setText(_translate("MainWindow", "Save(&S)"))
        self.action_A.setText(_translate("MainWindow", "Save as(&A)"))
        self.action_Z.setText(_translate("MainWindow", "Reset(&Z)"))
        self.action_C.setText(_translate("MainWindow", "Copy(&C)"))
        self.action_T.setText(_translate("MainWindow", "Reset toolbar(&T)"))
        self.action_L.setText(_translate("MainWindow", "To Chinese(&L)"))
        self.action_Q.setText(_translate("MainWindow", "Quit(&Q)"))
        self.action_B.setText(_translate("MainWindow", "About(&B)"))
        self.action_V.setText(_translate("MainWindow", "Open camera(&V)"))

    def set_toolbar(self):
        self.toolBar = QToolBar()
        self.addToolBar(self.toolBar)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/save.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.action_S.setIcon(icon1)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("images/open.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.action_O.setIcon(icon2)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("images/copy.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.action_C.setIcon(icon3)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("images/reset.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.action_Z.setIcon(icon4)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("images/exit.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.action_Q.setIcon(icon5)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("images/save-as.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.action_A.setIcon(icon6)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("images/tools.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.action_T.setIcon(icon7)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap("images/translate.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.action_L.setIcon(icon8)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap("images/help.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.action_B.setIcon(icon9)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap("images/camera.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.action_V.setIcon(icon10)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap("images/left.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.action_left.setIcon(icon11)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap("images/right.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.action_right.setIcon(icon12)
        self.toolBar.addAction(self.action_O)
        self.toolBar.addAction(self.action_V)
        self.toolBar.addAction(self.action_S)
        self.toolBar.addAction(self.action_A)
        self.toolBar.addAction(self.action_left)
        self.toolBar.addAction(self.action_right)

    def save_image(self):
        suffix = self.img_path.split(".")[1]
        self.image.save(self.img_path, suffix, 100)

    def save_as_image(self):
        file_dir = os.path.dirname(self.img_path)
        file_path = QFileDialog.getSaveFileName(
            self,
            "保存文件",
            file_dir,
            "Image Files (*.png *.jpg *.bmp *.jpeg)"
        )
        if file_path[0]:
            suffix = file_path[0].split(".")[1]
            self.image.save(file_path[0], suffix, 100)

    @staticmethod
    def about_message():
        message = QMessageBox()
        message.setText(
            "本软件基于PyQt & Python-OpenCV，由Shine 209050926开发。\ngithub: https://github.com/happy-shine/ShinePS")
        message.setWindowTitle("关于本软件")
        message_icon = QPixmap("images/about.jpeg")
        message_icon = message_icon.scaled(
            100,
            100,
            Qt.AspectRatioMode.KeepAspectRatio
        )
        message.setIconPixmap(message_icon)
        message.exec()

    def open_camera(self):
        self.img_path = ''
        if not self.timer_camera.isActive():
            self.camera_model, ok = QInputDialog.getText(self, '选择相机模式',
                                                         '不输入为原始相机，输入1为边缘检测，输入2为二值化，输入3为灰度化')
            if ok:
                if self.camera_model == '0':
                    self.camera_model = 0
                elif self.camera_model == '1':
                    self.camera_model = 1
                elif self.camera_model == '2':
                    self.camera_model = 2
                elif self.camera_model == '3':
                    self.camera_model = 3
                else:
                    self.camera_model = 0
                flag = self.cap.open(self.CAM_NUM)
                if not flag:
                    QtWidgets.QMessageBox.Warning(self, u'Warning', u'请检测相机与电脑是否连接正确',
                                                  buttons=QtWidgets.QMessageBox.StandardButton.Ok,
                                                  defaultButton=QtWidgets.QMessageBox.StandardButton.Ok)
                else:
                    self.timer_camera.start(30)

        else:
            self.timer_camera.stop()
            self.cap.release()
            self.img_label.clear()

    def show_camera(self):
        flag, image_read = self.cap.read()
        show = cv2.cvtColor(image_read, cv2.COLOR_BGR2RGB)
        if self.camera_model == 0:
            self.image = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format.Format_RGB888)

        elif self.camera_model == 1:
            gray = cv2.cvtColor(image_read, cv2.COLOR_BGR2GRAY)
            show = cv2.Canny(gray, 100, self.edge_slider.value() * 8)
            self.image = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format.Format_Grayscale8)

        elif self.camera_model == 2:
            gray = cv2.cvtColor(image_read, cv2.COLOR_BGR2GRAY)
            ret, show = cv2.threshold(
                gray,
                self.binarization_slider.value(),
                255,
                cv2.THRESH_BINARY
            )
            self.image = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format.Format_Grayscale8)

        elif self.camera_model == 3:
            show = cv2.cvtColor(image_read, cv2.COLOR_BGR2GRAY)
            self.image = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format.Format_Grayscale8)
        self.update_image()
