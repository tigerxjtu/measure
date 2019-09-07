#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, QMenu, QAction, qApp, QMessageBox, QDialog, QComboBox, QLabel, QDialogButtonBox,QGridLayout
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal, QPoint, QRect
from PyQt5.QtGui import QPainter, QColor, QPalette, QBrush, QPen
from PyQt5 import QtGui
from common import *
from abc import ABCMeta, abstractmethod
import cv2
import sys
# from ui.dialog import Ui_Dialog

measure_items_front=['F脖子上L','F脖子上R',
               'F脖子下L','F脖子下R',
               'F左肩','F右肩',
               'F左手腕L', 'F左手腕R',
               'F右手腕L', 'F右手腕R',
               'F脚底L', 'F脚底R',
               'F胸部L', 'F胸部R',
               'F腰部L', 'F腰部R',
               'F臀部L', 'F臀部R']

measure_items_side=['S脖子上L','S脖子上R',
                    'S脖子下L','S脖子下R',
                    'S胸部L','S胸部R',
                    'S腰部L','S腰部R',
                    'S臀部L','S臀部R']

measure_mapping={'F脖子上':'f_neck_up',
               'F脖子下':'f_neck_down',
               'F左肩':'f_shoulder_left',
                'F右肩':'f_shoulder_right',
               'F左手腕':'f_wrist_left',
               'F右手腕': 'f_wrist_right',
               'F脚底':'f_foot_down',
               'F胸部':'f_xiong',
               'F腰部':'f_yao',
               'F臀部': 'f_tun',
                'S脖子上': 's_neck_up',
                'S脖子下': 's_neck_down',
                'S胸部':'s_xiong',
                'S腰部':'s_yao',
                'S臀部': 's_tun'
}

orig_size = (1080,1440)
dst_size = (540,720)
ratio=0.5

def is_one_line(left_point,right_point,cur_point):
    left_x, left_y = left_point
    right_x, right_y = right_point
    cur_x,cur_y = cur_point
    if left_x==right_x:
        return cur_x==left_x
    dx=right_x-left_x
    dy=right_y-left_y
    y_pos=(cur_x-left_x)*dy/dx+left_y
    return cur_y==int(y_pos)

class Body(object):
    __metaclass__ = ABCMeta # 必须先声明

    def __init__(self, body_id):
        self.body_id = body_id
        self.tag = None #F or B  正面、侧面
        self.outline = [] #轮廓点
        self.features = {} #采集的特征点
        self.img_file=None #人像文件
        self.outline_file = None #轮廓点文件
        self.img = None #合成图象

    @abstractmethod
    def load_file(self):
        pass

    def load_outline(self):
        self.load_file()
        self.outline = get_points(self.outline_file)

    def load_feature(self):
        file_path=os.path.join(path3,'%s%s.json'%(self.body_id,self.tag))
        if os.path.exists(file_path):
            with open(file_path) as fp:
                self.features=json.load(fp)

    def process_img(self):
        self.load_file()
        self.img = cv2.imread(self.img_file)
        self.load_outline()
        self.load_feature()
        for point in self.outline:
            cv2.circle(self.img, point, 1, (0, 0, 255))

    def get_result_img(self):
        return self.img

    def cut_outline_points(self,left_point, right_point):
        left_x,left_y=left_point
        right_x,right_y= right_point
        cent_x = (left_x+right_x)//2
        points=filter(lambda x:is_one_line(left_point,right_point,x),self.outline)
        print(left_point,right_point)
        cut_left,cut_right = None,None
        for p in points:
            print(p)
            if p[0]<=cent_x:
                if cut_left is None:
                    cut_left = p
                else:
                    cut_left = p if cut_left[0]<p[0] else cut_left
            else:
                if cut_right is None:
                    cut_right = p
                else:
                    cut_right = p if cut_right[0]>p[0] else cut_right
        return cut_left,cut_right

    def cut_points(self,pt_left,pt_right,str_pos):
        left_point,right_point=self.cut_outline_points(pt_left,pt_right)
        if left_point is not None and right_point is not None:
            self.features['%s_%s'%(measure_mapping[str_pos],'L')]=left_point
            self.features['%s_%s'%(measure_mapping[str_pos],'R')]=right_point
            return True
        return False


class FrontBody(Body):

    def __init__(self,body_id):
        super().__init__(body_id)
        self.tag='F'

    def load_file(self):
        self.outline_file,self.img_file = get_file_name(self.body_id,'F')


class SideBody(Body):

    def __init__(self,body_id):
        super().__init__(body_id)
        self.tag='S'

    def load_file(self):
        self.outline_file,self.img_file = get_file_name(self.body_id,'S')


class BodyFrame(QFrame):
    msg2Statusbar = pyqtSignal(str)

    def __init__(self,parent,tag='F'):
        super().__init__(parent)
        self.resize(dst_size[0],dst_size[1])
        self.start_point,self.end_point=None,None
        self.tag = tag

    def set_body(self, body_id):
        self.body_id = body_id
        if self.tag == 'F':
            self.body = FrontBody(self.body_id)
        else:
            self.body = SideBody(self.body_id)
        self.body.process_img()
        img = self.body.get_result_img()
        img = cv2.resize(img,dst_size)
        # img = img[:,:,::-1]
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # print(img.shape)
        showImage=QtGui.QImage(img.data, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888)
        self.pix_img= QtGui.QPixmap.fromImage(showImage)
        # palette = QPalette()
        # palette.setBrush(self.backgroundRole(),QBrush(pix_img))
        # self.resize(500,750)
        # self.setPalette(palette)
        self.update()

    def save_feature(self):
        file_path=os.path.join(path3,'%s%s.json'%(self.body_id,self.tag))
        with open(file_path,'w') as fp:
            json.dump(self.body.features,fp)

    def create_front_menu(self):
        self.op_menu = QMenu(self)
        self.f_neck_up = self.op_menu.addAction("F脖子上")
        self.f_neck_down = self.op_menu.addAction("F脖子下")
        self.f_shoulder = self.op_menu.addAction("F肩膀")
        self.f_xiong = self.op_menu.addAction("F胸部")
        self.f_yao = self.op_menu.addAction("F腰部")
        self.f_tun = self.op_menu.addAction("F臀部")
        self.f_wrist_left = self.op_menu.addAction("F左手腕")
        self.f_wrist_right = self.op_menu.addAction("F右手腕")
        self.act_clear = self.op_menu.addAction("Clear")

    def create_side_menu(self):
        self.op_menu = QMenu(self)
        self.s_neck_up = self.op_menu.addAction("S脖子上")
        self.s_neck_down = self.op_menu.addAction("S脖子下")
        self.s_xiong = self.op_menu.addAction("S胸部")
        self.s_yao = self.op_menu.addAction("S腰部")
        self.s_tun = self.op_menu.addAction("S臀部")
        self.act_clear = self.op_menu.addAction("Clear")

    def clear_line(self):
        self.start_point=None
        self.end_point=None
        self.update()

    def move_line(self,dx,dy):
        # print('before:',self.start_point.x(),self.start_point.y())
        self.start_point.setX(self.start_point.x()+dx)
        self.start_point.setY(self.start_point.y() + dy)
        self.end_point.setX(self.end_point.x()+dx)
        self.end_point.setY(self.end_point.y()+dy)
        # print('end:', self.start_point.x(), self.start_point.y())
        self.update()

    def cut_points(self,str_pos):
        if not (self.start_point and self.end_point):
            QMessageBox.information(self, '提醒', '先划线，再采集特征点')
            return
        pt1=(int(self.start_point.x()/ratio),int(self.start_point.y()/ratio))
        pt2=(int(self.end_point.x()/ratio),int(self.end_point.y()/ratio))
        if self.body.cut_points(pt1,pt2,str_pos):
            self.clear_line()
            return
        else:
            QMessageBox.information(self, '提醒', '划线范围有误')

    def contextMenuEvent(self, e):
        if not self.body:
            return
        if not self.op_menu:
            self.msg2Statusbar.emit('context menu not created!')
            return
        action = self.op_menu.exec_(self.mapToGlobal(e.pos()))
        if action == self.act_clear:
            self.clear_line()
            return
        # QMessageBox.information(self,'title',action.text())
        if action:
            self.cut_points(action.text())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()#point.x(),point.y()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:  # 这里只能用buttons(), 因为button()在mouseMoveEvent()中无论
            self.end_point = event.pos()  # 按下什么键，返回的都是Qt::NoButton
            # self.painter.begin(self)  # 注意这里的参数必须是self.pix，涂鸦只能在这个300*300的白板上进行
            # self.painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            # self.painter.drawLine(self.start_point, self.end_point)
            # self.painter.end()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.end_point = event.pos()
            self.update()

    def keyPressEvent(self, event):
        # print('keyPressEvent')
        key=event.key()
        if key==Qt.Key_Left:
            dx,dy=-1,0
        elif key==Qt.Key_Right:
            dx,dy=1,0
        elif key==Qt.Key_Up:
            dx,dy=0,-1
        elif key==Qt.Key_Down:
            dx,dy=0,1
        else:
            super(BodyFrame, self).keyPressEvent(event)
        self.move_line(dx,dy)

    def paintEvent(self, event):
        if not self.body:
            return
        painter = QPainter(self)
        painter.drawPixmap(0, 0, dst_size[0], dst_size[1],self.pix_img);
        pen = QPen(Qt.red, 2, Qt.SolidLine)
        if self.start_point and self.end_point:
            painter.setPen(pen)
            painter.drawLine(self.start_point,self.end_point)
        pt_pen = QPen(Qt.blue, 3, Qt.SolidLine)
        for point in self.body.features.values():
            x,y=point
            upper_left=QPoint(int(x*ratio-2),int(y*ratio-2))
            down_right=QPoint(int(x*ratio+2),int(y*ratio+2))
            painter.setPen(pt_pen)
            painter.drawEllipse(QRect(upper_left,down_right))

class MyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
        # self.exec()

    def initUI(self):
        self.setWindowTitle("选择人体")  # 窗口标题
        self.setGeometry(400, 400, 300, 400)  # 窗口位置与大小

        self.lab_a = QLabel('人体id:')

        # self.name_edit = QLineEdit()  # 用于接收用户输入的单行文本输入框
        self.bodies = QtWidgets.QComboBox(self)  # 建立一个下拉列表框
        self.bodies.resize(250,250)

        for i,name in enumerate(names):  # 为下拉列表框添加选择项（从数据库中查询取得）
            self.bodies.addItem(str(i+1)+'--'+name, name)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  # 窗口中建立确认和取消按钮
        self.glayout = QGridLayout()
        self.glayout.addWidget(self.lab_a, 0, 0)
        # self.glayout.addWidget(self.lab_b, 1, 0)
        # self.glayout.addWidget(self.name_edit, 0, 1)
        self.glayout.addWidget(self.bodies, 1, 0)
        self.glayout.addWidget(self.buttons, 2, 0)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.setLayout(self.glayout)

    def get_data(self,index=0):
        return self.bodies.itemData(self.bodies.currentIndex())


class MainUI(QMainWindow):

    def __init__(self):
        super().__init__()
        self.body_id=None
        self.initUI()


    def initUI(self):

        self.statusbar = self.statusBar()
        self.init_body_frame()
        # self.set_body('U1002217190901092403591')

        # self.resize(dst_size[0],dst_size[1]+50)
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QRect(20, 740, 100, 30))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText('打开')
        self.pushButton_2 = QtWidgets.QPushButton(self)
        self.pushButton_2.setGeometry(QRect(150, 740, 100, 30))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setText('保存')
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QRect(280, 740, 30, 12))
        self.label.setObjectName("label")
        self.label.setText('id:')
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setGeometry(QRect(320, 740, 300, 30))

        self.pushButton.clicked.connect(self.show_dialog)
        self.pushButton_2.clicked.connect(self.save_features)

        self.create_dialog()

        self.set_body(self.body_id)

        self.resize(1200,800)
        self.center()
        self.setWindowTitle('Body')

        # self.tboard.show()
        self.show()

    def set_body(self,body_id):
        # if not self.fboard:
        #     self.init_body_frame()
        self.lineEdit.setText(body_id)
        self.fbody.set_body(body_id)
        self.sbody.set_body(body_id)

    def init_body_frame(self):
        self.fbody = BodyFrame(self)
        # self.fboard.set_body('U1002217190901092403591')
        self.fbody.create_front_menu()
        # self.setCentralWidget(self.fboard)
        self.fbody.setGeometry(QRect(10, 10, 540, 720))

        self.sbody = BodyFrame(self, 'S')
        self.sbody.create_side_menu()
        self.sbody.setGeometry(QRect(570, 10, 540, 720))

        self.fbody.msg2Statusbar[str].connect(self.statusbar.showMessage)
        self.sbody.msg2Statusbar[str].connect(self.statusbar.showMessage)

    def create_dialog(self):
        # self.dialog = QDialog(self)
        # self.d=Ui_Dialog()
        # self.d.setupUi(self.dialog)
        # for name in names:
        #     if not self.body_id:
        #         self.body_id=name
        #     self.d.comboBox.addItem(name,name)
        self.dialog=MyDialog()
        self.body_id=self.dialog.get_data()


    def show_dialog(self):
        if self.dialog.exec():
            # self.body_id=self.d.get_data()
            self.body_id=self.dialog.get_data()
            # print(self.body_id)
            if self.body_id:
                self.set_body(self.body_id)

    def save_features(self):
        self.fbody.save_feature()
        self.sbody.save_feature()

    def keyPressEvent(self, event):
        # print('keypress in mainwin')
        if not self.fbody:
            # self.set_body('U1002217190901092403591')
            return
        if self.fbody.start_point and self.fbody.end_point:
            self.fbody.keyPressEvent(event)
            return
        if self.sbody.start_point and self.sbody.end_point:
            self.sbody.keyPressEvent(event)

    def center(self):
        screen=QDesktopWidget().screenGeometry()
        size=self.geometry()
        self.move((screen.width()-size.width())//2, (screen.height()-size.height())//2)


if __name__ == '__main__':
    app=QApplication([])
    ui=MainUI()
    # self.set_body('U1002217190901092403591')
    # ui.set_body('U1002217190901092403591')
    sys.exit(app.exec_())