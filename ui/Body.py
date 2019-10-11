from abc import ABCMeta, abstractmethod
import cv2
import numpy as np
from common import *
# from train_data import get_file_name
from file_name import get_file_name
# from db_client import get_file_name
from BodyFeature import min_angle_feature,min_feature,min_distance_angle,round_int,min_y_pt,get_outline_distribute,speed_delta,range_outline
from utils import x_inersect_y

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

    def get_main_range(self):
        left, right = self.bdfeatureXY['left_hip'], self.bdfeatureXY['right_hip']
        y_down = round_int((left[1] + right[1]) / 2)
        x0 = round_int((left[0] + right[0]) / 2)
        if self.tag == 'F' or self.tag == 'B':
            left,right =self.auto_features['ye_L'],self.auto_features['ye_R']
            y_up = int(max(left[1],right[1]))
        else:
            left,right = self.bdfeatureXY['left_shoulder'],self.bdfeatureXY['right_shoulder']
            y_up = int(min(left[1],right[1]))
        return y_up,y_down,x0

    def get_main_range2(self):
        left, right = self.bdfeatureXY['left_hip'], self.bdfeatureXY['right_hip']
        y_down = round_int((left[1] + right[1]) / 2)

        left,right = self.bdfeatureXY['left_shoulder'],self.bdfeatureXY['right_shoulder']
        x0 = round_int((left[0] + right[0]) / 2)
        y_up = round_int((left[1] + right[1]) / 2)
        return y_up,y_down,x0


    def get_main_distances(self):
        y_up, y_down, x0 = self.get_main_range()
        distances = get_outline_distribute(self.outline,y_up,y_down,x0)
        if self.tag =='S':
            return distances
        left, right = self.auto_features['shoulder_L'], self.auto_features['shoulder_R']
        y_start = max(left[1],right[1])
        x0 = round_int((left[0] + right[0]) / 2)
        bot_left,bot_right = self.cut_by_y(y_up,x0)
        up_distances = [x_inersect_y(right,bot_right,y)-x_inersect_y(left,bot_left,y) for y in range(y_start,y_up)]
        return up_distances+distances

    def get_main_distances2(self):
        distances = self.get_main_distances()
        split_index = int(len(distances)/2)
        return distances[:split_index],distances[split_index:]

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
        try:
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
        except Exception as e:
            print(e)
            print('load pre feature fails:', self.body_id)

    def load_export_features(self):
        self.bottom_y = self._max_y
        self.foot_y = self.bottom_y - 110
        auto_features = self.calculate_features()
        # print(auto_features.keys())
    # ['neck_L', 'neck_R', 'shoulder_L', 'shoulder_R', 'ye_L', 'ye_R', 'tun_L', 'tun_R', 'huiyin', 'xiong_L',
    #            'xiong_R', 'yao_L', 'yao_R']
    # ['neck_L', 'neck_R', 'tun_L', 'tun_R', 'xiong_L', 'xiong_R', 'yao_L', 'yao_R']
        if self.tag=='F':
            y_neck_up = auto_features['neck_R'][1] - 8
            y_neck_down = auto_features['neck_R'][1] + 8
            x0_neck =  (auto_features['neck_L'][0] + auto_features['neck_R'][0])//2
            self.features['f_neck_up_L'],self.features['f_neck_up_R'] = self.cut_by_y(y_neck_up,x0_neck)
            self.features['f_neck_down_L'], self.features['f_neck_down_R'] = self.cut_by_y(y_neck_down, x0_neck)
            self.huiyin_point = auto_features['huiyin']
            self.center_x = self.huiyin_point[0]
            self.features['f_shoulder_L'],self.features['f_shoulder_R']=auto_features['shoulder_L'],auto_features['shoulder_R']
            self.features['f_yewo_L'], self.features['f_yewo_R'] = auto_features['ye_L'], auto_features['ye_R']
            # f_wrist_left_L,f_wrist_right_R
            y_left,y_right = self.left_finger[1]-90, self.right_finger[1]-90
            self.features['f_wrist_left_L'],_ = self.cut_by_y_out(y_left)
            _,self.features['f_wrist_right_R'] = self.cut_by_y_out(y_right)


        if self.tag=='S':
            self.center_x = (self._min_x+self._max_x)//2
            self.features['s_yao_L'],self.features['s_yao_R']=auto_features['yao_L'],auto_features['yao_R']
            self.features['s_tun_L'], self.features['s_tun_R'] = auto_features['tun_L'], auto_features['tun_R']
            self.features['s_neck_up_L'],self.features['s_neck_up_R'] = auto_features['neck_L'], auto_features['neck_R']
            self.features['s_xiong_L'],self.features['s_xiong_R'] = auto_features['xiong_L'], auto_features['xiong_R']



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
        y_up, y_down, x0 = self.get_main_range2()  # shoulder, hip
        # yao
        r = 2.8
        y = int((y_up + r * y_down) / (1 + r))
        features['yao_L'], features['yao_R'] = self.cut_by_y(y, x0)
        #xiong
        r=0.25

        y = int((y_up + r * y_down) / (1 + r))
        if self.tag == 'S':
            features['xiong_L'],features['xiong_R'] = self.cut_by_y(y, x0)
        else:
            try:
                left, right = features['shoulder_L'], features['shoulder_R']
                bot_left, bot_right = features['ye_L'],features['ye_R']
                if y<bot_left[1]:
                    xiong_L = (x_inersect_y(left,bot_left,y),y)
                else:
                    xiong_L = self.cut_by_y(y, x0)[0]
                if y<bot_right[1]:
                    xiong_R = (x_inersect_y(right, bot_right, y),y)
                else:
                    xiong_R = self.cut_by_y(y, x0)[1]
                bot_left, bot_right = features['yao_L'], features['yao_R']
                xiong_L_new = (x_inersect_y(left, bot_left, y), y)
                xiong_R_new = (x_inersect_y(right, bot_right, y), y)
                if xiong_L[0]>xiong_L_new[0]:
                    features['xiong_L'] = xiong_L
                else:
                    features['xiong_L'] = xiong_L_new

                if xiong_R[0]<xiong_R_new[0]:
                    features['xiong_R'] = xiong_R
                else:
                    features['xiong_R'] = xiong_R_new

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
            # print(shoulder_L,shoulder_R)
            # self.other_points.append(self.left_shoulder_feature(self.bdfeatureXY['right_shoulder']))
            # self.other_points.append(self.right_shoulder_feature(self.bdfeatureXY['left_shoulder']))

            return shoulder_L[0],shoulder_R[0]
        if self.tag == 'B':
            shoulder_L = min_distance_angle(self.outline, self.bdfeatureXY['left_shoulder'], -0.8)
            shoulder_L = shoulder_L[0], shoulder_L[1] if shoulder_L else None
            shoulder_R = min_distance_angle(self.outline, self.bdfeatureXY['right_shoulder'], 0.8)
            shoulder_R = shoulder_R[0], shoulder_R[1] if shoulder_R else None

            # self.other_points.append(self.left_shoulder_feature(self.bdfeatureXY['left_shoulder']))
            # self.other_points.append(self.right_shoulder_feature(self.bdfeatureXY['right_shoulder']))

            return shoulder_L[0], shoulder_R[0]

    def left_shoulder_feature(self,left_shoulder,min_y_range=20):
        x,y = left_shoulder
        x,y = int(x),int(y)
        up,_=self.cut_by_x(x)
        if y-up[1]<min_y_range:
            y=up[1]+min_y_range
        left,_ = self.cut_by_y_out(y)
        points = range_outline(self.outline,up,left)
        speeds=speed_delta(points)
        index = np.argmax(np.abs(speeds))
        print(index)
        self.add_other_points(up)
        self.add_other_points(left)
        # print(speeds)
        return points[index]

    def right_shoulder_feature(self,right_shoulder,min_y_range=20):
        x, y = right_shoulder
        x, y = int(x), int(y)
        up, _ = self.cut_by_x(x)
        if y - up[1] < min_y_range:
            y = up[1] + min_y_range
        _, right = self.cut_by_y_out(y)
        points = range_outline(self.outline, up, right)
        speeds = speed_delta(points)
        speeds2=[]
        for i in range(len(speeds)):
            if i==0:
                speeds2.append(speeds[i])
            else:
                speeds2.append(speeds[i]+speeds[i-1])
        index = np.argmax(np.abs(speeds2))
        self.add_other_points(up)
        self.add_other_points(right)
        return points[index]


    def process_hip_feature(self):
        left, right = self.bdfeatureXY['left_hip'], self.bdfeatureXY['right_hip']
        y0 = round_int((left[1] + right[1]) / 2)
        x0 = round_int((left[0] + right[0]) / 2)
        return self.cut_by_y(y0,x0)

    #0.25 (shoulder, xiong, hip)
    # def process_xiong_feature(self, r=0.25):
    #     y_up,y_down,x0 = self.get_main_range2() #shoulder, hip
    #     y = int((y_up+r*y_down)/(1+r))
    #     if self.tag == 'S':
    #         return self.cut_by_y(y,x0)
    #
    #     left, right = self.auto_features['shoulder_L'], self.auto_features['shoulder_R']
    #     y_start = max(left[1], right[1])
    #     x0 = round_int((left[0] + right[0]) / 2)
    #     bot_left, bot_right = self.cut_by_y(y_up, x0)



    def get_result_img(self):
        return self.img

    def cut_by_x(self,x0):
        # print(x0)
        # print(len(self.outline))
        points = filter(lambda x: x[0] == x0, self.outline)
        points = list(points)
        # print(points)
        up = min(points, key=lambda x: x[1])
        down = max(points, key=lambda x: x[1])
        return up, down

    def cut_by_y_out(self,y):
        points = filter(lambda x: x[1] == y, self.outline)
        points = list(points)
        left = min(points, key=lambda x: x[0])
        right = max(points, key=lambda x: x[0])
        return left, right


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