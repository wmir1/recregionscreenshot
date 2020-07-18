from PySide2.QtGui import QMouseEvent, QPixmap, QColor, QWindow, QScreen, QGuiApplication, QPainter, QPen, QCursor, QStandardItemModel, QStandardItem
from PySide2.QtCore import QPoint, Qt, Slot, QSize, QTimer, QEvent, QRect, QStandardPaths, QDir
import sys
from PySide2.QtWidgets import \
    QApplication, QLabel, QWidget, QGraphicsDropShadowEffect,\
    QPushButton, QMainWindow, QCheckBox, QVBoxLayout,\
    QHBoxLayout, QSizePolicy, QSpinBox, QDialog, QFileDialog, QMessageBox, QTabWidget, QComboBox, QTextEdit, QSplitter, QStatusBar

from datetime import datetime
import os
import logging
from shutil import rmtree


logging.basicConfig(level=logging.WARNING,
                    format='[%(levelname)s] - %(asctime)s - %(message)s')


class CheckableComboBox(QComboBox):
    def addItem(self, item):
        super(CheckableComboBox, self).addItem(item)
        item = self.model().item(self.count()-1, 0)
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setCheckState(Qt.Unchecked)

    def item_checked(self, index):
        item = self.model().item(index, 0)
        return item.checkState() == Qt.Checked

    def set_item_check(self, item_text,state):
        for i in range(self.count()):
            item = self.model().item(i, 0)
            if self.itemText(i) == item_text:
                if state:
                    item.setCheckState(Qt.Checked)
                elif not state:
                    item.setCheckState(Qt.UnChecked)
                # list_checked.append(self.itemText(i))

    def list_item_checked(self):
        list_checked = []
        for i in range(self.count()):
            item = self.model().item(i, 0)
            if item.checkState() == Qt.Checked:
                list_checked.append(self.itemText(i))
        if not list_checked:
            list_checked.append('eng')
        return list_checked


class Screenshot(QWidget):
    def __init__(self):
        super().__init__()
        self.init_UI()

    def init_UI(self):
        splitter = QSplitter(Qt.Horizontal)
        splitter.splitterMoved.connect(self.resizeEvent)
        # hor_layout = QHBoxLayout()
        self.original_pixmap = QPixmap()

        self.screenshot_label = QLabel(self)
        self.screenshot_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.screenshot_label.setAlignment(Qt.AlignCenter)
        self.screenshot_label.resize(
            self.size().width()*0.45, self.screenshot_label.size().height())

        self.text_edit = QTextEdit()

        splitter.addWidget(self.screenshot_label)
        splitter.addWidget(self.text_edit)

        self.save_screenshot_button = QPushButton("Save Screenshot", self)
        self.save_screenshot_button.clicked.connect(self.save_screenshot)

        self.save_text_button = QPushButton("Save Text", self)
        self.save_text_button.setEnabled(False)
        self.save_text_button.clicked.connect(self.save_text)

        self.take_rect_screenshoot_button = QPushButton(
            'Take region screenshoot', self)
        self.take_rect_screenshoot_button.clicked.connect(
            self.create_rect_screenshot)

        self.quit_screenshot_button = QPushButton("Quit", self)
        self.quit_screenshot_button.clicked.connect(QApplication.quit)

        screenshot_buttons_layout = QHBoxLayout()

        screenshot_buttons_layout.addWidget(self.save_screenshot_button)
        screenshot_buttons_layout.addWidget(self.save_text_button)
        screenshot_buttons_layout.addWidget(self.quit_screenshot_button)

        # screenshot_buttons_layout.addStretch()

        self.lang_combo_box = CheckableComboBox()
        self.lang_combo_box.addItem("eng")
        self.lang_combo_box.addItem("ukr")
        self.lang_combo_box.addItem("rus")
        self.lang_combo_box.set_item_check("eng",True)
        

        self.recognition_button = QPushButton('Recognize', self)
        self.recognition_button.setEnabled(False)
        self.recognition_button.clicked.connect(self.run_recognition)

        self.negative_check_box = QCheckBox('Negative')
        self.negative_check_box.setToolTip(
            'Make negative picture for better recognition')
        self.grayscale_check_box = QCheckBox('Grayscale')
        self.grayscale_check_box.setChecked(True)
        self.grayscale_check_box.setToolTip(
            'Make grayscale picture for better recognition')

        recognition_buttons_layout = QHBoxLayout()

        recognition_buttons_layout.addWidget(self.take_rect_screenshoot_button)
        recognition_buttons_layout.addWidget(self.recognition_button)
        recognition_buttons_layout.addWidget(self.lang_combo_box)
        recognition_buttons_layout.addWidget(self.negative_check_box)
        recognition_buttons_layout.addWidget(self.grayscale_check_box)

        main_layout = QVBoxLayout(self)

        main_layout.addWidget(splitter)
        main_layout.addLayout(recognition_buttons_layout)
        main_layout.addLayout(screenshot_buttons_layout)

        self.setLayout(main_layout)
        self.shoot_screen()
        self.setWindowTitle("Screenshot recognition")
        self.resize(600, 600)
        self.screenshot_size = []

    @Slot()
    def new_screenshot(self):
        if self.hide_this_window_check_box.isChecked():
            self.hide()
        self.new_screenshot_button.setDisabled(True)
        if self.delay_spin_box.value() != 0:
            QTimer.singleShot(self.delay_spin_box.value()
                              * 1000, self.shoot_screen)
        else:
            QTimer.singleShot(100, self.shoot_screen)

    @Slot()
    def save_screenshot(self):
        frmat = '.png'
        initial_path = QStandardPaths.writableLocation(
            QStandardPaths.PicturesLocation)
        if not initial_path:
            initial_path = QDir.currentPath()
        initial_path += '/Screenshot-' + \
            str(datetime.now()).replace(' ', '_') + frmat
        file_dialog = QFileDialog(self, "Save as", initial_path)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        if file_dialog.exec() != QDialog.Accepted:
            return
        file_name = file_dialog.selectedFiles()[0]
        if not self.original_pixmap.save(file_name):
            logging.error("The image could not be saved to \"{}\".".format(
                QDir.toNativeSeparators(file_name)))
            QMessageBox.warning(self, "Save Error", "The image could not be saved to \"{}\".".format(
                QDir.toNativeSeparators(file_name)))

    @Slot()
    def save_text(self):
        frmat = '.txt'
        initial_path = QStandardPaths.writableLocation(
            QStandardPaths.DocumentsLocation)
        if not initial_path:
            initial_path = QDir.currentPath()
        initial_path += '/Screenshot_Text-' + \
            str(datetime.now()).replace(' ', '_') + frmat
        file_dialog = QFileDialog(self, "Save as", initial_path)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        if file_dialog.exec() != QDialog.Accepted:
            return
        file_name = file_dialog.selectedFiles()[0]
        with open(file_name, 'w') as wf:
            wf.write(self.text_edit.toPlainText())

    @Slot()
    def create_rect_screenshot(self):
        self.recognition_button.setEnabled(True)
        self.new_window = FullScreenDraw(self)

        # if self.hide_this_window_check_box.isChecked():
        self.hide()
        self.new_window.showFullScreen()
        # self.show()

    @Slot()
    def run_recognition(self):
        folder_path = 'temp_img'
        logging.debug("running recognition")
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
            logging.debug("Directory " + folder_path + " created")
        else:
            logging.debug("Directory " + folder_path + " already yet")
        if self.original_pixmap.save(folder_path + '/img001.png'):
            logging.debug("Picture img001 created")

            logging.debug("List_item_checked: " +
                          str(self.lang_combo_box.list_item_checked()))

            res = self.recognition(
                folder_path + '/img001.png', self.lang_combo_box.list_item_checked())
            # calling reco
            # print(res)

            self.text_edit.setText(res)
            self.save_text_button.setEnabled(True)
            if not res:
                QMessageBox.information(
                    self, "Recognition failed", "Can't recognize text")
            else:
                QMessageBox.information(
                    self, "Recognition  complete", "Recognition complete")

        try:
            rmtree(folder_path)
            logging.debug("Directory " + folder_path+" deleted")
            # logging.debug("Picture img001 created")
        except OSError as e:
            logging.error("Error: %s : %s" % (folder_path, e.strerror))

    def recognition(self, path, langs=['eng']):
        try:
            from PIL import Image, ImageOps
        except ImportError:
            import Image
        import pytesseract
        srt_lang = '+'.join(langs)
        im = Image.open(path)
        if self.negative_check_box.isChecked():
            im = ImageOps.invert(im.convert('RGB'))
        if self.grayscale_check_box.isChecked():
            im = im.convert('LA')
            # im.save('test.png', 'PNG')
        res = pytesseract.image_to_string(im, lang=srt_lang)
        return res

    @Slot()
    def shoot_screen(self, windo=0):
        screen = QGuiApplication.primaryScreen()
        window = QWindow()
        window = self.windowHandle()
        if window:
            screen = window.screen()
        if not screen:
            return

        # if self.delay_spin_box.value() != 0:
        #     QApplication.beep()

        if type(windo) in (list, tuple):
            self.original_pixmap = screen.grabWindow(
                QApplication.desktop().winId(), *windo)
        else:
            self.original_pixmap = screen.grabWindow(
                QApplication.desktop().winId(), windo)
        self.update_screenshot_label()

        # self.new_screenshot_button.setDisabled(False)
        # if self.hide_this_window_check_box.isChecked():
        self.show()

    def update_screenshot_label(self):
        self.screenshot_label.setPixmap(self.original_pixmap.scaled(self.screenshot_label.size(),
                                                                    Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def resizeEvent(self, event):
        scaled_size = QSize()
        scaled_size = self.original_pixmap.size()
        scaled_size.scale(self.screenshot_label.size(), Qt.KeepAspectRatio)
        if scaled_size != self.screenshot_label.pixmap().size():
            self.update_screenshot_label()


class FullScreenDraw(QDialog):
    def __init__(self, parent=None):
        super(FullScreenDraw, self).__init__(parent)
        self.setCursor(QCursor(Qt.CrossCursor))

        self.mouse_pressed = False
        self.draw_started = False

        self.m_pix = QPixmap(400, 200)

        self.m_pix.fill(Qt.transparent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.cursor_pos = []

        self.m_rect = QRect()
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

    def mousePressEvent(self, event):
        # self.showFullScreen()

        self.mouse_pressed = True
        self.m_rect.setTopLeft(event.pos())
        self.m_rect.setBottomRight(event.pos())
        self.mouse_start_pos = (event.globalX(), event.globalY())
        self.update()

    def mouseMoveEvent(self, event):
        if event.type() == QEvent.MouseMove:
            self.m_rect.setBottomRight(event.pos())
        self.update()

    def fix_coordinate(self, fp_coordinate, sp_coordinate):
        if fp_coordinate == sp_coordinate:
            sp_coordinate = (sp_coordinate[0]+50, sp_coordinate[1]+50)
        fp = (min(fp_coordinate[0], sp_coordinate[0])+2,
              (min(fp_coordinate[1], sp_coordinate[1])+2))
        sp = (max(fp_coordinate[0], sp_coordinate[0]),
              (max(fp_coordinate[1], sp_coordinate[1])))

        return fp[0], fp[1], sp[0]-fp[0], sp[1]-fp[1]

    def mouseReleaseEvent(self, event):
        if event.type() == QEvent.MouseButtonRelease:
            self.mouse_end_pos = (event.globalX(), event.globalY())
        self.mouse_pressed = False
        self.update()
        self.cursor_pos = self.fix_coordinate(
            self.mouse_start_pos, self.mouse_end_pos)

        # print(self.cursor_pos, '----', self.mouse_start_pos, self.mouse_end_pos)
        self.parent().shoot_screen(self.cursor_pos)
        self.parent().show()

        self.close()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        # painter.setOpacity(0)
        pen = QPen(Qt.red, 1, Qt.SolidLine)
        painter.setPen(pen)
        if self.mouse_pressed:
            painter.drawPixmap(0, 0, self.m_pix)
            painter.drawRect(self.m_rect)
            self.draw_started = True
        elif self.draw_started:
            temp_painter = QPainter(self.m_pix)
            temp_painter.setPen(pen)
            # self.painter.drawPixmap(0, 0, self.m_pix)
            temp_painter.drawRect(self.m_rect)
            painter.drawPixmap(0, 0, self.m_pix)
            self.draw_started = False
        painter.end()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    screenshot = Screenshot()
    screenshot.move(
        screenshot.screen().availableGeometry().topLeft() + QPoint(20, 20))
    screenshot.show()

    app.exec_()
