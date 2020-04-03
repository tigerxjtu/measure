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
from feature_export import FeatureTan
from outline_export import OutlineTransformer,OutlineTan
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
               'F肩部':'f_shoulder',
               'F左手腕':'f_wrist_left',
               'F右手腕': 'f_wrist_right',
               'F脚底':'f_foot_down',
                'F腋窝':'f_yewo',
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

        self.center_x = None
        self.foot_y = None
        self.bottom_y = None

        self._min_x = None
        self._max_x = None
        self._min_y = None
        self._max_y = None

        self.left_finger=None
        self.right_finger=None
        self.center_head_point = None
        self.top_head_point = None

        self.huiyin_point = None

        self.other_points=[]

    @abstractmethod
    def load_file(self):
        pass

    def clear_other_points(self):
        self.other_points.clear()

    def add_other_points(self,pt):
        self.other_points.append(pt)

    def load_outline(self):
        self.load_file()
        _,_,self.outline = get_points(self.outline_file)
        p = min(self.outline, key=lambda x: x[0])
        self._min_x = p[0]
        if self.tag=='F':
            self.left_finger = p
        p = max(self.outline, key=lambda x: x[0])
        self._max_x = p[0]
        if self.tag=='F':
            self.right_finger = p
        p = min(self.outline, key=lambda x: x[1])
        self._min_y = p[1]
        self.top_head_point=p
        p = max(self.outline, key=lambda x: x[1])
        self._max_y = p[1]


    def load_feature(self):
        file_path=os.path.join(path3,'%s%s.json'%(self.body_id,self.tag))
        if os.path.exists(file_path):
            with open(file_path) as fp:
                all_features=json.load(fp)
                self.features=all_features.get('points',{})
                self.center_x=all_features['center_x']
                self.foot_y = all_features['foot_y']
                self.bottom_y = all_features['bottom_y']
                self.top_head_point = all_features['top_head']
                if self.tag=='F':
                    self.left_finger=all_features['finger_left']
                    self.right_finger = all_features['finger_right']
                    self.huiyin_point = all_features['huiyin_point']

    def process_img(self):
        self.load_file()
        self.img = cv2.imread(self.img_file)
        self.load_outline()
        self.load_feature()
        for point in self.outline:
            cv2.circle(self.img, point, 1, (0, 0, 255))

    def get_result_img(self):
        return self.img

    def cut_by_y(self, y):
        points = filter(lambda x: x[1]==y, self.outline)
        cut_left, cut_right = None, None
        for p in points:
            print(p)
            if p[0] <= self.center_x:
                if cut_left is None:
                    cut_left = p
                else:
                    cut_left = p if cut_left[0] < p[0] else cut_left
            else:
                if cut_right is None:
                    cut_right = p
                else:
                    cut_right = p if cut_right[0] > p[0] else cut_right
        return cut_left, cut_right

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


    def set_height(self, h):
        self.height = h



    def get_cord_pos(self):
        return self._min_x, self._max_x, self.center_x, self.foot_y , self.bottom_y

    def set_bottom_point(self,bottom_y):
        if not self.foot_y and not self.center_x:
            return False
        self.bottom_y=bottom_y
        return True

class FrontBody(Body):

    def __init__(self,body_id):
        super().__init__(body_id)
        self.tag='F'

    def load_file(self):
        self.outline_file,self.img_file = get_file_name(self.body_id,'F')

    def set_foot_point(self,cent_x,cent_y):
        points = filter(lambda x: x[0] == cent_x, self.outline)
        points = list(points)
        if len(points)<2:
            return False
        self.huiyin_point= max(points, key=lambda x: x[1])
        self.center_head_point= min(points, key=lambda x: x[1])

        self.center_x=cent_x
        self.foot_y=cent_y
        if not self.bottom_y:
            self.bottom_y=self._max_y
        return True

    def get_body_features(self):
        features={}
        features['points']=self.features
        features['top_head']=self.top_head_point
        features['center_x']=self.center_x
        features['foot_y']=self.foot_y
        features['bottom_y']=self.bottom_y
        features['finger_left']=self.left_finger
        features['finger_right']=self.right_finger
        features['huiyin_point']=self.huiyin_point
        return features


class SideBody(Body):

    def __init__(self,body_id):
        super().__init__(body_id)
        self.tag='S'

    def load_file(self):
        self.outline_file,self.img_file = get_file_name(self.body_id,'S')

    def set_foot_point(self, cent_x, cent_y):
        self.center_x = cent_x
        self.foot_y = cent_y
        if not self.bottom_y:
            self.bottom_y = self._max_y
        return True

    def get_body_features(self):
        features={}
        features['points']=self.features
        features['top_head']=self.top_head_point
        features['center_x']=self.center_x
        features['foot_y']=self.foot_y
        features['bottom_y']=self.bottom_y

        return features


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
            json.dump(self.body.get_body_features(),fp)

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

        pt_pen = QPen(Qt.blue, 3, Qt.SolidLine)
        painter.setPen(pt_pen)
        for point in self.body.features.values():
            x,y=point
            upper_left=QPoint(int(x*ratio-2),int(y*ratio-2))
            down_right=QPoint(int(x*ratio+2),int(y*ratio+2))
            painter.drawEllipse(QRect(upper_left,down_right))
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

        pt_pen = QPen(Qt.green, 3, Qt.SolidLine)
        painter.setPen(pt_pen)
        for pt in self.body.other_points:
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

        self.pushButton.clicked.connect(self.show_dialog)
        self.pushButton_2.clicked.connect(self.save_features)
        self.pushButton_3.clicked.connect(self.export_features)
        self.pushButton_4.clicked.connect(self.display_other_features)

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

    def display_other_features(self):
        exporter = FeatureTan(self.fbody.body, self.sbody.body)
        exporter.map_front2side(['f_neck_up_L','f_neck_down_L'])
        self.sbody.update()

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