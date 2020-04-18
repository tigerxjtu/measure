#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, QMenu, QAction, qApp, QMessageBox, QDialog, QComboBox, QLabel, QDialogButtonBox,QGridLayout
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal, QPoint, QRect
from PyQt5.QtGui import QPainter, QColor, QPalette, QBrush, QPen
from PyQt5 import QtGui
from common import *
from train_data import *
from abc import ABCMeta, abstractmethod
import cv2
import sys
from ui.feature_export import FeatureTan
from ui.outline_export import OutlineTransformer,OutlineTan
from BodyFeature import min_angle_feature,min_feature
from model.NeckModel import NeckModel
from ui.Body import Body,FrontBody,SideBody,BackBody
from analysis.neck_data import build_user_info
from model.ShoulderModel import ShoulderModel
user_info = build_user_info()

orig_size = (1080,1440)
dst_size = (540,720)
ratio=0.5

class BodyFrame(QFrame):
    msg2Statusbar = pyqtSignal(str)

    def __init__(self,parent,tag='F'):
        super().__init__(parent)
        self.resize(dst_size[0],dst_size[1])
        self.start_point,self.end_point=None,None
        self.tag = tag
        self.op_menu = None

    def set_body(self, body_id):
        self.body_id = body_id
        if self.tag == 'F':
            self.body = FrontBody(self.body_id)
        elif self.tag == 'S':
            self.body = SideBody(self.body_id)
        else:
            self.body = BackBody(self.body_id)
        self.body.process_display_img()
        self.body.load_pre_feature()

        # self.body.calculate_features()
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
            # print(self.body.get_body_features())
            str = json.dumps(self.body.get_body_features())
            fp.write(str)

    def create_front_menu(self):
        self.op_menu = QMenu(self)
        self.f_neck_up = self.op_menu.addAction("F脖子上")
        self.f_neck_down = self.op_menu.addAction("F脖子下")
        self.f_shoulder = self.op_menu.addAction("F肩部")
        self.f_yewo = self.op_menu.addAction("F腋窝")
        self.f_xiong = self.op_menu.addAction("F胸部")
        self.f_yao = self.op_menu.addAction("F腰部")
        self.f_tun = self.op_menu.addAction("F臀部")
        self.f_wrist_left = self.op_menu.addAction("F左手腕")
        self.f_wrist_right = self.op_menu.addAction("F右手腕")
        self.f_foot = self.op_menu.addAction('F足底')
        self.f_bottom = self.op_menu.addAction('F底部')
        self.act_clear = self.op_menu.addAction("Clear")

    def create_side_menu(self):
        self.op_menu = QMenu(self)
        self.s_neck_up = self.op_menu.addAction("S脖子上")
        self.s_neck_down = self.op_menu.addAction("S脖子下")
        self.s_xiong = self.op_menu.addAction("S胸部")
        self.s_yao = self.op_menu.addAction("S腰部")
        self.s_tun = self.op_menu.addAction("S臀部")
        self.f_foot = self.op_menu.addAction('S足底')
        self.f_bottom = self.op_menu.addAction('S底部')
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

    def get_center_point(self):
        pt1 = (int(self.start_point.x() / ratio), int(self.start_point.y() / ratio))
        pt2 = (int(self.end_point.x() / ratio), int(self.end_point.y() / ratio))
        return (pt1[0]+pt2[0])//2, (pt1[1]+pt2[1])//2

    def contextMenuEvent(self, e):
        try:
            if not self.body:
                return
            if not self.op_menu:
                self.msg2Statusbar.emit('context menu not created!')
                return
            if not self.start_point and not self.end_point:
                self.msg2Statusbar.emit('请先完成标定')
                return
            action = self.op_menu.exec_(self.mapToGlobal(e.pos()))
            if action == self.act_clear:
                self.clear_line()
                self.releaseKeyboard()
                return
            if action == self.f_foot:
                cent_x,cent_y=self.get_center_point()
                if not self.body.set_foot_point(cent_x,cent_y):
                    QMessageBox.information(self, 'title', '足底标定有误')
                self.clear_line()
                self.releaseKeyboard()
                return
            if action == self.f_bottom:
                cent_x, cent_y = self.get_center_point()
                if not self.body.set_bottom_point(cent_y):
                    QMessageBox.information(self, 'title', '请先完成足底标定')
                self.clear_line()
                self.releaseKeyboard()
                return
            # QMessageBox.information(self,'title',action.text())
            if action:
                self.cut_points(action.text())
            self.releaseKeyboard()
        except Exception as e:
            print(e)


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
        self.msg2Statusbar.emit('{},{}'.format(event.pos().x()/ratio,event.pos().y()/ratio))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.end_point = event.pos()
            self.update()
            self.grabKeyboard()

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
        try:
            if not self.body:
                return
            painter = QPainter(self)
            painter.drawPixmap(0, 0, dst_size[0], dst_size[1],self.pix_img);
            pen = QPen(Qt.red, 2, Qt.SolidLine)
            if self.start_point and self.end_point:
                painter.setPen(pen)
                painter.drawLine(self.start_point,self.end_point)
                cent_x=(self.start_point.x()+self.end_point.x())//2
                cent_y=(self.start_point.y()+self.end_point.y())//2
                painter.drawLine(cent_x,cent_y,cent_x,0)

            # pt_pen = QPen(Qt.blue, 3, Qt.SolidLine)
            # painter.setPen(pt_pen)
            # for point in self.body.features.values():
            #     x,y=point
            #     upper_left=QPoint(int(x*ratio-2),int(y*ratio-2))
            #     down_right=QPoint(int(x*ratio+2),int(y*ratio+2))
            #     painter.drawEllipse(QRect(upper_left,down_right))
            if self.body.top_head_point:
                x, y = self.body.top_head_point
                upper_left = QPoint(int(x * ratio - 2), int(y * ratio - 2))
                down_right = QPoint(int(x * ratio + 2), int(y * ratio + 2))
                painter.drawEllipse(QRect(upper_left, down_right))
            if self.body.left_finger:
                x, y = self.body.left_finger
                upper_left = QPoint(int(x * ratio - 2), int(y * ratio - 2))
                down_right = QPoint(int(x * ratio + 2), int(y * ratio + 2))
                painter.drawEllipse(QRect(upper_left, down_right))
            if self.body.left_finger:
                x, y = self.body.right_finger
                upper_left = QPoint(int(x * ratio - 2), int(y * ratio - 2))
                down_right = QPoint(int(x * ratio + 2), int(y * ratio + 2))
                painter.drawEllipse(QRect(upper_left, down_right))
            if self.body.huiyin_point:
                x, y = self.body.huiyin_point
                upper_left = QPoint(int(x * ratio - 2), int(y * ratio - 2))
                down_right = QPoint(int(x * ratio + 2), int(y * ratio + 2))
                painter.drawEllipse(QRect(upper_left, down_right))
            #

            pt_pen = QPen(Qt.green, 3, Qt.SolidLine)
            painter.setPen(pt_pen)
            last_pt = None
            for pt in self.body.other_points:
                x, y = pt
                if last_pt:
                    upper_left = QPoint(int(x * ratio - 2), int(y * ratio - 2))
                    down_right = QPoint(int(x * ratio + 2), int(y * ratio + 2))
                else:
                    upper_left = QPoint(int(x * ratio - 4), int(y * ratio - 4))
                    down_right = QPoint(int(x * ratio + 4), int(y * ratio + 4))
                painter.drawEllipse(QRect(upper_left, down_right))
                last_pt = pt
            if last_pt:
                pt_pen = QPen(Qt.red, 3, Qt.SolidLine)
                painter.setPen(pt_pen)
                x, y = last_pt
                upper_left = QPoint(int(x * ratio - 4), int(y * ratio - 4))
                down_right = QPoint(int(x * ratio + 4), int(y * ratio + 4))
                painter.drawEllipse(QRect(upper_left, down_right))


            # pt_pen = QPen(Qt.green, 3, Qt.SolidLine)
            # painter.setPen(pt_pen)
            # for pt in self.body.featureXY.values():
            #     x, y = pt
            #     upper_left = QPoint(int(x * ratio - 2), int(y * ratio - 2))
            #     down_right = QPoint(int(x * ratio + 2), int(y * ratio + 2))
            #     painter.drawEllipse(QRect(upper_left, down_right))

            # keys = self.body.bdfeatureXY.keys()
            # keys = ['left_hip','left_shoulder']
            # pt_pen = QPen(Qt.red, 3, Qt.SolidLine)
            # painter.setPen(pt_pen)
            # # for pt in self.body.bdfeatureXY.values():
            # for key in keys:
            #     if key not in self.body.bdfeatureXY:
            #         continue
            #     pt = self.body.bdfeatureXY[key]
            #     x, y = pt
            #     upper_left = QPoint(int(x * ratio - 2), int(y * ratio - 2))
            #     down_right = QPoint(int(x * ratio + 2), int(y * ratio + 2))
            #     painter.drawEllipse(QRect(upper_left, down_right))

            # keys = ['right_hip', 'right_shoulder']
            # pt_pen = QPen(Qt.yellow, 3, Qt.SolidLine)
            # painter.setPen(pt_pen)
            # # for pt in self.body.bdfeatureXY.values():
            # for key in keys:
            #     if key not in self.body.bdfeatureXY:
            #         continue
            #     pt = self.body.bdfeatureXY[key]
            #     x, y = pt
            #     upper_left = QPoint(int(x * ratio - 2), int(y * ratio - 2))
            #     down_right = QPoint(int(x * ratio + 2), int(y * ratio + 2))
            #     painter.drawEllipse(QRect(upper_left, down_right))

            pt_pen = QPen(Qt.cyan, 3, Qt.SolidLine)
            painter.setPen(pt_pen)
            for key,pt in self.body.auto_features.items():
                # print(key)
                if pt:
                    # print(key,pt)
                    x, y = pt
                    upper_left = QPoint(int(x * ratio - 2), int(y * ratio - 2))
                    down_right = QPoint(int(x * ratio + 2), int(y * ratio + 2))
                    painter.drawEllipse(QRect(upper_left, down_right))

            min_x, max_x, center_x, foot_y, bottom_y =self.body.get_cord_pos()
            if foot_y:
                cord_pen = QPen(Qt.blue, 2, Qt.SolidLine)
                painter.setPen(cord_pen)
                painter.drawLine(min_x* ratio,bottom_y* ratio,max_x* ratio,bottom_y* ratio)
                painter.drawLine(min_x* ratio, foot_y* ratio, max_x* ratio, foot_y* ratio)
                painter.drawLine(center_x* ratio,bottom_y* ratio,center_x* ratio,0)

            colors = [Qt.yellow,Qt.darkYellow,Qt.darkBlue,Qt.darkGreen,Qt.darkRed]
            extra = self.body.extra
            if extra:
                for i in range(len(extra)):
                    color = colors[i%len(colors)]
                    pen = QPen(color, 2, Qt.SolidLine)
                    painter.setPen(pen)
                    head = True
                    for pt in extra[i]:
                        x, y = pt
                        if not head:
                            upper_left = QPoint(int(x * ratio - 1), int(y * ratio - 1))
                            down_right = QPoint(int(x * ratio + 1), int(y * ratio + 1))
                        else:
                            upper_left = QPoint(int(x * ratio - 3), int(y * ratio - 3))
                            down_right = QPoint(int(x * ratio + 3), int(y * ratio + 3))
                            head = False
                        painter.drawEllipse(QRect(upper_left, down_right))
        except Exception as e:
            print(e)



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
        self.pushButton.setGeometry(QRect(40, 740, 100, 30))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText('打开')
        self.pushButton_2 = QtWidgets.QPushButton(self)
        self.pushButton_2.setGeometry(QRect(150, 740, 100, 30))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setText('保存')
        self.pushButton_3 = QtWidgets.QPushButton(self)
        self.pushButton_3.setGeometry(QRect(260, 740, 100, 30))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setText('导出')

        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QRect(380, 740, 30, 12))
        self.label.setObjectName("label")
        self.label.setText('id:')
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setGeometry(QRect(420, 740, 300, 30))

        self.pushButton_4 = QtWidgets.QPushButton(self)
        self.pushButton_4.setGeometry(QRect(760, 740, 100, 30))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setText('显示')

        self.btn_prev = QtWidgets.QPushButton(self)
        self.btn_prev.setGeometry(QRect(880, 740, 100, 30))
        self.btn_prev.setObjectName("btn_prev")
        self.btn_prev.setText('上一条')

        self.btn_next = QtWidgets.QPushButton(self)
        self.btn_next.setGeometry(QRect(1000, 740, 100, 30))
        self.btn_next.setObjectName("btn_next")
        self.btn_next.setText('下一条')

        self.btn_test = QtWidgets.QPushButton(self)
        self.btn_test.setGeometry(QRect(1120, 740, 100, 30))
        self.btn_test.setObjectName("btn_test")
        self.btn_test.setText('测试')

        self.btn_outline = QtWidgets.QPushButton(self)
        self.btn_outline.setGeometry(QRect(1240, 740, 100, 30))
        self.btn_outline.setObjectName("btn_outline")
        self.btn_outline.setText('轮廓')

        # self.btn_compute = QtWidgets.QPushButton(self)
        # self.btn_compute.setGeometry(QRect(1120, 740, 100, 30))
        # self.btn_compute.setObjectName("btn_compute")
        # self.btn_compute.setText('计算')
        #
        # self.lbl1 = QtWidgets.QLabel(self)
        # self.lbl1.setGeometry(QRect(1120, 10, 40, 30))
        # # self.lbl1.setObjectName("lbl_neck")
        # self.lbl1.setText('颈围:')
        # self.lbl_neck = QtWidgets.QLabel(self)
        # self.lbl_neck.setGeometry(QRect(1170, 10, 40, 30))
        # # self.lbl_neck.setObjectName("lbl_neck")
        # # self.lbl_neck.setText('')
        # self.edit_neck = QtWidgets.QLineEdit(self)
        # self.edit_neck.setGeometry(QRect(1120, 45, 100, 30))
        #
        # self.lbl2 = QtWidgets.QLabel(self)
        # self.lbl2.setGeometry(QRect(1120, 100, 40, 30))
        # self.lbl2.setText('肩宽:')
        # self.lbl_shoulder = QtWidgets.QLabel(self)
        # self.lbl_shoulder.setGeometry(QRect(1170, 100, 40, 30))
        #
        # self.edit_shoulder = QtWidgets.QLineEdit(self)
        # self.edit_shoulder.setGeometry(QRect(1120, 135, 100, 30))

        self.pushButton.clicked.connect(self.show_dialog)
        self.pushButton_2.clicked.connect(self.save_features)
        self.pushButton_3.clicked.connect(self.export_features)
        self.pushButton_4.clicked.connect(self.display_other_features)
        self.btn_prev.clicked.connect(self.prev_body)
        self.btn_next.clicked.connect(self.next_body)
        # self.btn_compute.clicked.connect(self.compute)
        self.btn_test.clicked.connect(self.test_click)
        self.btn_outline.clicked.connect(self.outline_click)


        self.create_dialog()

        self.set_body(self.body_id)

        self.resize(1680,820)
        self.center()
        self.setWindowTitle('Body')

        # self.tboard.show()
        self.show()

    def set_body(self,body_id):
        # if not self.fboard:
        #     self.init_body_frame()
        self.body_id = body_id
        self.lineEdit.setText(body_id)
        self.fbody.set_body(body_id)
        self.sbody.set_body(body_id)
        self.bbody.set_body(body_id)

    def init_body_frame(self):
        self.fbody = BodyFrame(self)
        # self.fboard.set_body('U1002217190901092403591')
        self.fbody.create_front_menu()
        # self.setCentralWidget(self.fboard)
        self.fbody.setGeometry(QRect(10, 10, 540, 720))

        self.sbody = BodyFrame(self, 'S')
        self.sbody.create_side_menu()
        self.sbody.setGeometry(QRect(570, 10, 540, 720))

        self.bbody = BodyFrame(self, 'B')
        # self.sbody.create_side_menu()
        self.bbody.setGeometry(QRect(1120, 10, 540, 720))

        self.fbody.msg2Statusbar[str].connect(self.statusbar.showMessage)
        self.sbody.msg2Statusbar[str].connect(self.statusbar.showMessage)
        self.bbody.msg2Statusbar[str].connect(self.statusbar.showMessage)

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

    def display_other_features(self):
        try:
            exporter = FeatureTan(self.fbody.body, self.sbody.body)
            exporter.map_front2side(['f_neck_up_L','f_neck_down_L'])
            self.sbody.update()
        except Exception as e:
            print(e)

    def prev_body(self):
        try:
            cur_id = names.index(self.body_id)
            if cur_id < 0:
                cur_id = 0
            if cur_id>0:
                self.set_body(names[cur_id-1])
            if cur_id==0:
                self.set_body(names[-1])
        except Exception as e:
            print(e)

    def next_body(self):
        try:
            cur_id = names.index(self.body_id)
            if cur_id < 0:
                cur_id = 0
            length = len(names)
            cur_id = (cur_id+1)%length
            self.set_body(names[cur_id])
        except Exception as e:
            print(e)

    def test_click(self):
        # if self.sbody.start_point and self.sbody.end_point:
        #     x1,y1 = int(self.sbody.start_point.x() / ratio), int(self.sbody.start_point.y() / ratio)
        #     x2,y2 = int(self.sbody.end_point.x() / ratio), int(self.sbody.end_point.y() / ratio)
        #     y = int((y1+y2)/2)
        #     y_up,y_down,_=self.sbody.body.get_main_range()
        #     r = (y-y_up)/(y_down-y)
        #     self.statusbar.showMessage('%d,%d,%d---%f'%(y_up,y,y_down,r))
        try:
            body_id=self.lineEdit.text()
            self.set_body(body_id.strip())
        except Exception as e:
            print(e)



    def outline_click(self):
        try:
            outline_exp = OutlineTan(self.fbody.body, self.sbody.body)
            # front_curves = outline_exp.front_curves()
            # self.fbody.body.set_extra(front_curves)
            # side_curves = outline_exp.side_curves()
            # self.sbody.body.set_extra(side_curves)
            # self.fbody.body.other_points=outline_exp.front_points()
            # self.sbody.body.other_points = outline_exp.side_points()
            self.other_points = outline_exp.front_points()
            self.s_other_points = outline_exp.side_points()

            # cnt = 0
            # for pt in other_points:
            #     cnt += 1
            #     if cnt==10:
            #         time.sleep(0.1)
            #         cnt=0
            #     self.fbody.body.other_points.append(pt)
            #     self.fbody.update()
            self.timer_id = self.startTimer(100, timerType=Qt.VeryCoarseTimer)
            self.other_index=0
            self.length = len(self.other_points)
            # self.sbody.update()
            # self.s_other_index = 0
            self.s_length = len(self.s_other_points)
        except Exception as e:
            print(e)

    def timerEvent(self, event):
        for i in range(10):
            if self.other_index>=self.length:
                self.killTimer(self.timer_id)
                self.timer_id = 0
                break
            pt = self.other_points[self.other_index]
            self.fbody.body.other_points.append(pt)
            if self.other_index < self.s_length:
                pt = self.s_other_points[self.other_index]
                self.sbody.body.other_points.append(pt)
            self.other_index+=1
        self.fbody.update()
        self.sbody.update()

    def compute(self):
        try:
            ud = user_info[self.body_id]
            height = ud['height']
            model = NeckModel(self.body_id,height)
            neck = model.predict()
            self.edit_neck.setText(str(round(neck,2)))
            self.lbl_neck.setText(str(ud['neck']))

            model = ShoulderModel(self.body_id, height)
            shoulder = model.predict()
            self.edit_shoulder.setText(str(round(shoulder, 2)))
            self.lbl_shoulder.setText(str(ud['shoulder']))
        except Exception as e:
            print(e)
            QMessageBox.information(self, 'error',str(e))


    def export_features(self):
        try:
            exporter = FeatureTan(self.fbody.body, self.sbody.body)
            file_path = os.path.join(path3, '%s_FL.txt' % (self.body_id))
            exporter.write_file(file_path)
        except Exception as e:
            print(e)
            QMessageBox.information(self, 'error',str(e))
        try:
            # outline_transformer=OutlineTransformer(self.fbody.body.outline,self.fbody.body.top_head_point)
            # curves = outline_transformer.scan()
            # curves = outline_transformer.merge_curves(curves)
            # curve = outline_transformer.force_connect(curves)
            # outline_transformer = OutlineTransformer(self.sbody.body.outline, self.sbody.body.top_head_point)
            # curves = outline_transformer.scan()
            # curves = outline_transformer.merge_curves(curves)
            # curve = outline_transformer.force_connect(curves)

            # file_path = os.path.join(path3, '%s_PT.txt' % (self.body_id))
            # with open(file_path, 'w') as fp:
            #     json.dump(points,fp)
            outline_exp = OutlineTan(self.fbody.body, self.sbody.body)
            file_path = os.path.join(path3, '%s_FC.txt' % (self.body_id))
            outline_exp.export_front(file_path)
            file_path = os.path.join(path3, '%s_SC.txt' % (self.body_id))
            outline_exp.export_side(file_path)
        except Exception as e:
            print(e)
            QMessageBox.information(self, 'error',str(e))

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