from abc import ABCMeta, abstractmethod
import cv2
from common import *
# from train_data import get_file_name
from file_name import get_file_name
# from db_client import get_file_name
from BodyFeature import min_angle_feature,min_feature,min_distance_angle,round_int,min_y_pt

# bd_path = r'C:\projects\python\measure\ui\data\bd'
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


def is_one_line(left_point,right_point,cur_point):
    left_x, left_y = left_point
    right_x, right_y = right_point
    cur_x,cur_y = cur_point
    if left_x==right_x:
        return cur_x==left_x
    dx=right_x-left_x
    dy=right_y-left_y
    y_pos=int(round((cur_x-left_x)*dy/dx+left_y,0))
    return cur_y==int(y_pos)

class Body(object):
    __metaclass__ = ABCMeta # 必须先声明

    def __init__(self, body_id,folder=None,person_id=None):
        self.folder = folder
        self.person_id = person_id
        # print(self.folder,self.person_id)

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

        self.neck_left_L = None
        self.neck_left_R = None

        self.featureXY = {}
        self.bdfeatureXY = {}

        self.auto_features={}

    @abstractmethod
    def load_file(self):
        pass

    def clear_other_points(self):
        self.other_points.clear()

    def add_other_points(self,pt):
        self.other_points.append(pt)

    def load_outline(self):
        self.load_file()
        self.outline = get_points(self.outline_file)
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

    def load_pre_feature(self):
        if self.folder:
            file = os.path.join(path1,self.folder, '%s%s2.txt' % (self.body_id, self.tag))
        else:
            file = os.path.join(path1, '%s%s2.txt' % (self.body_id, self.tag))
        with open(file) as f:
            content = f.read()
            data = json.loads(content)
            points = data['featureXY']
            self.featureXY = {p['pos']:(int(p['x']), int(p['y'])) for p in points}
        if self.folder:
            out_file = os.path.join(path1,self.folder, '%s%s1.json' % (self.body_id, self.tag))
        else:
            out_file =os.path.join(path1,'%s%s1.json' % (self.body_id, self.tag))
        with open(out_file, 'r') as fp:
            self.bdfeatureXY = json.load(fp)

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
        self.load_pre_feature()
        self.proces_neck_feature()
        for point in self.outline:
            cv2.circle(self.img, point, 1, (0, 0, 255))

    def process_display_img(self):
        self.load_file()
        self.img = cv2.imread(self.img_file)
        self.load_outline()
        self.load_pre_feature()
        # self.proces_neck_feature()
        self.calculate_features()
        for point in self.outline:
            cv2.circle(self.img, point, 1, (0, 0, 255))

    def calculate_features(self):
        features = {}
        neck_feature = self.proces_neck_feature()
        if neck_feature:
            features['neck_L'],features['neck_R']=neck_feature

        shoulder_feature = self.process_shoulder_feature()
        if shoulder_feature:
            features['shoulder_L'], features['shoulder_R']=shoulder_feature
            try:
                x_left,x_right = features['shoulder_L'][0],features['shoulder_R'][0]
                d = int((x_right - x_left)/3)
                x1,x2 = x_left+d,x_right-d
                features['ye_L']=min_y_pt(self.outline,x_left-2,x1,features['shoulder_L'][1]+5)
                features['ye_R'] = min_y_pt(self.outline, x2, x_right+2, features['shoulder_R'][1]+5)
                # print(features['ye_L'],features['ye_R'])
            except Exception as e:
                print(e)

        left,right = self.process_hip_feature()
        features['tun_L'],features['tun_R'] = left,right
        if self.tag == 'F' or self.tag=='B':
            try:
                x_left, x_right = features['tun_L'][0], features['tun_R'][0]
                d = int((x_right - x_left) / 3)
                x1, x2 = x_left + d, x_right - d
                features['huiyin']=min_y_pt(self.outline, x1,x2, features['tun_R'][1])
            except Exception as e:
                print(e)


        self.auto_features = features
        # print(features)
        return features



    def proces_neck_feature(self):
        low,up = 0.08, 0.22
        if self.tag == 'F' or self.tag == 'B':
            result = min_feature(self.outline,low,up,self._min_y, self._max_y)
            # print(result)
            if result:
                x1,x2,y = result
                self.features['neck_left_L']=[int(x1),int(y)]
                self.features['neck_left_R'] = [int(x2),int(y)]
                # self.neck_left_L = [int(x1),int(y)]
                # self.neck_left_R = [int(x2),int(y)]
                # print((y-self._min_y)/(self._max_y-self._min_y))
                return self.features['neck_left_L'],self.features['neck_left_R']
        if self.tag == 'S':
            result = min_angle_feature(self.outline,low,up,self._min_y, self._max_y,0.3)
            if result:
                # print(result)
                left,right,dis = result
                self.features['neck_left_L'] = [int(left[0]),int(left[1])]
                self.features['neck_left_R'] = [int(right[0]),int(right[1])]
                # self.neck_left_L = [int(left[0]),int(left[1])]
                # self.neck_left_R = [int(right[0]),int(right[1])]
                return self.features['neck_left_L'], self.features['neck_left_R']

    def process_shoulder_feature(self):
        if self.tag == 'F':
            shoulder_L = min_distance_angle(self.outline, self.bdfeatureXY['right_shoulder'],-0.8)
            shoulder_L = shoulder_L[0],shoulder_L[1] if shoulder_L else None
            shoulder_R = min_distance_angle(self.outline, self.bdfeatureXY['left_shoulder'],0.8)
            shoulder_R = shoulder_R[0], shoulder_R[1] if shoulder_R else None
            return shoulder_L[0],shoulder_R[0]
        if self.tag == 'B':
            shoulder_L = min_distance_angle(self.outline, self.bdfeatureXY['left_shoulder'], -0.8)
            shoulder_L = shoulder_L[0], shoulder_L[1] if shoulder_L else None
            shoulder_R = min_distance_angle(self.outline, self.bdfeatureXY['right_shoulder'], 0.8)
            shoulder_R = shoulder_R[0], shoulder_R[1] if shoulder_R else None
            return shoulder_L[0], shoulder_R[0]

    def process_hip_feature(self):
        left, right = self.bdfeatureXY['left_hip'], self.bdfeatureXY['right_hip']
        y0 = round_int((left[1] + right[1]) / 2)
        x0 = round_int((left[0] + right[0]) / 2)
        return self.cut_by_y(y0,x0)



    def get_result_img(self):
        return self.img

    def cut_by_y(self, y, x0=None):
        points = filter(lambda x: x[1]==y, self.outline)
        cut_left, cut_right = None, None
        if not x0:
            x0=self.center_x
        for p in points:
            # print(p)
            if p[0] <= x0:
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
        # print(left_point,right_point)
        cut_left,cut_right = None,None
        for p in points:
            # print(p)
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

    def __init__(self,body_id,*args):
        super().__init__(body_id,*args)
        self.tag='F'

    def load_file(self):
        if not self.folder:
            # print(self.body_id)
            self.outline_file,self.img_file = get_file_name(self.body_id,'F')
        else:
            self.outline_file, self.img_file = get_file_name(self.body_id, 'F',self.folder)

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
        features['neck_left_L'] = self.neck_left_L
        features['neck_left_R'] = self.neck_left_R
        return features


class SideBody(Body):

    def __init__(self,body_id,*args):
        super().__init__(body_id,*args)
        self.tag='S'

    def load_file(self):
        if not self.folder:
            self.outline_file,self.img_file = get_file_name(self.body_id,'S')
        else:
            self.outline_file, self.img_file = get_file_name(self.body_id, 'S',self.folder)

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

class BackBody(Body):

    def __init__(self,body_id,*args):
        super().__init__(body_id,*args)
        self.tag='B'

    def load_file(self):
        if not self.folder:
            self.outline_file,self.img_file = get_file_name(self.body_id,'B')
        else:
            self.outline_file, self.img_file = get_file_name(self.body_id, 'B',self.folder)

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

if __name__ == '__main__':
    pass