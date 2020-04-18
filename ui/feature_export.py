
from ui.PointTransformer import PtTransformer
from utils import distance,angle,cut_by_y


class FeatureTan(object):

    '''头顶:8.000000,544.000000
脖子r_top:19.000000,478.000000
脖子r_bot:19.000000,467.000000
肩膀R:63.881104,449.596375
手R:153.000000,238.000000
腋窝R:153.000000,238.000000
会阴:2.000000,231.000000
腋窝L:153.000000,238.000000
手L:-164.000000,267.000000
肩膀L:-59.921478,449.107025
脖子L_bot:-17.000000,467.000000
脖子L_top:-17.000000,478.000000
S头顶:-89.000000,537.000000
S腰R:-41.038361,333.572952
S臀R:-29.997406,280.501953
S脖子L_bot:-96.446259,450.670563
S脖子L_top:-99.005096,461.498177
脖子角度:0.364735
左臂长L:164.067710
右臂长R:168.082357
S胸R:-41.974915,412.525726
手腕L:-144.512512,309.373383
手腕R:134.977905,298.109039
真实脚高F:37.000000
真实脚高S:28.000000
像素身高F:544.000000
像素身高S:537.000000
    '''
    template ='''头顶:{}
脖子r_top:{}
脖子r_bot:{}
肩膀R:{}
手R:{}
腋窝R:{}
会阴:{}
腋窝L:{}
手L:{}
肩膀L:{}
脖子L_bot:{}
脖子L_top:{}
S头顶:{}
S腰R:{}
S臀R:{}
S脖子L_bot:{}
S脖子L_top:{}
脖子角度:{}
左臂长L:{}
右臂长R:{}
S胸R:{}
手腕L:{}
手腕R:{}
真实脚高F:{}
真实脚高S:{}
像素身高F:{}
像素身高S:{}
'''

    def __init__(self, front_body, side_body):
        self.front_body = front_body
        self.side_body = side_body
        self.data = []
        self._map={}
        self.init_map()

    def init_map(self):
        # self._map['']='top_x'  #'头顶x坐标',
        self._map['f_neck_R'] = 'neck_r_t'  # '右边脖子上x坐标',
        # self._map['f_neck_up_R']='neck_r_t' #'右边脖子上x坐标',
        self._map['f_neck_down_R']='neck_r_b' # '右边脖子下x坐标',
        self._map['f_shoulder_R']='shoulder_r' # '右边肩膀x坐标',
        # self._map['f_wrist_right_R']='hand_r' # '右边手尖x',
        self._map['f_yewo_R']='armpit_r' # '右边腋窝x坐标',
        # self._map['']='perineum_x' # '会阴x坐标',
        self._map['f_yewo_L']='armpit_l' # '左边腋窝x坐标',
        # self._map['f_wrist_left_L']='hand_l' # '左边手尖x',
        self._map['f_shoulder_L']='shoulder_l' # '左边肩膀x坐标',
        self._map['f_neck_down_L']='neck_l_b' # '左边脖子下x坐标',

        self._map['f_neck_L'] = 'neck_l_t'  # '左边脖子上x坐标',
        # self._map['f_neck_up_L']='neck_l_t' # '左边脖子上x坐标',
        # self._map['']='top_s_x' # '侧面头顶x坐标',
        self._map['s_xiong_R']='bust_s'
        # self._map['']='bust_s' # '侧面胸高交点x坐标',
        self._map['s_yao_R']='waist_s' # '侧面腰高交点x坐标',
        self._map['s_tun_R']='hip_s' # '侧面臀围高度交点x坐标',
        self._map['s_neck_up_L'] = 'neck_s_t'  # '侧面脖子上交点x坐标',
        self._map['s_neck_up_R'] = 'neck_s_b'  # '侧面脖子下交点x坐标',
        # self._map['s_neck_up_R'] = 'neck_s_t'  # '侧面脖子上交点x坐标',
        # self._map['s_neck_up_L'] = 'neck_s_b'  # '侧面脖子下交点x坐标',
        # self._map['']='neck_angle' # '侧面脖子角度',
        # self._map['']='foot_line' # '正面脚底线高度',
        # self._map['']='foot_line_s' # '侧面脚底线高度',

    def map_front2side(self,features):
        f_height = self.front_body.bottom_y - self.front_body.top_head_point[1]
        s_height = self.side_body.bottom_y - self.side_body.top_head_point[1]
        s_ratio = f_height / s_height
        f_ratio = s_height / f_height
        f_pf = PtTransformer(self.front_body.center_x, self.front_body.bottom_y)
        s_pf = PtTransformer(self.side_body.center_x, self.side_body.bottom_y)
        for feature in features:
            f_y = f_pf.transorm_y(self.front_body.features[feature][1]) * f_ratio
            s_y = int(round(s_pf.reverse_transform_y(f_y),0))
            left, right = self.side_body.cut_by_y(s_y)
            if left:
                self.side_body.add_other_points(left)
            if right:
                self.side_body.add_other_points(right)

    def map_front2side_feature(self,feature):
        f_height = self.front_body.bottom_y - self.front_body.top_head_point[1]
        s_height = self.side_body.bottom_y - self.side_body.top_head_point[1]
        s_ratio = f_height / s_height
        f_ratio = s_height / f_height
        f_pf = PtTransformer(self.front_body.center_x, self.front_body.bottom_y)
        s_pf = PtTransformer(self.side_body.center_x, self.side_body.bottom_y)
        f_y = f_pf.transorm_y(self.front_body.features[feature][1]) * f_ratio
        s_y = int(round(s_pf.reverse_transform_y(f_y), 0))
        left, right = self.side_body.cut_by_y(s_y)
        return left,right

    def write_file(self, file_path):
        # file_name = '%s_FL.txt'%self.front_body.body_id
        # file_name = os.path.join()
        with open(file_path, 'w') as fp:
            fp.write(FeatureTan.template.format(*self.output_data()))

    def output_data(self):
        self.data.clear()
        f_height=self.front_body.bottom_y - self.front_body.top_head_point[1]
        s_height=self.side_body.bottom_y - self.side_body.top_head_point[1]
        s_ratio=f_height/s_height
        f_ratio=s_height/f_height
        f_pf= PtTransformer(self.front_body.center_x,self.front_body.bottom_y)
        s_pf= PtTransformer(self.side_body.center_x,self.side_body.bottom_y)
        self.data.append(f_pf.transform_str(*self.front_body.top_head_point))#头顶
        self.data.append(f_pf.transform_str(*self.front_body.features['f_neck_up_R']))#脖子r_top
        self.data.append(f_pf.transform_str(*self.front_body.features['f_neck_down_R']))#脖子r_bot
        self.data.append(f_pf.transform_str(*self.front_body.features['f_shoulder_R']))#肩膀R
        self.data.append(f_pf.transform_str(*self.front_body.right_finger))#手R
        self.data.append(f_pf.transform_str(*self.front_body.features['f_yewo_R']))#腋窝R
        self.data.append(f_pf.transform_str(*self.front_body.huiyin_point))  # 会阴
        self.data.append(f_pf.transform_str(*self.front_body.features['f_yewo_L']))  # 腋窝L
        self.data.append(f_pf.transform_str(*self.front_body.left_finger))  # 手L
        self.data.append(f_pf.transform_str(*self.front_body.features['f_shoulder_L']))  # 肩膀L
        self.data.append(f_pf.transform_str(*self.front_body.features['f_neck_down_L']))  # 脖子L_bot
        self.data.append(f_pf.transform_str(*self.front_body.features['f_neck_up_L']))  # 脖子L_top

        self.data.append(s_pf.transform_str(*self.side_body.top_head_point))  # S头顶
        self.data.append(s_pf.transform_str(*self.side_body.features['s_yao_R']))  # S腰R
        self.data.append(s_pf.transform_str(*self.side_body.features['s_tun_R']))  # S臀R

        #S脖子L_bot
        f_neck_bot_y = f_pf.transorm_y(self.front_body.features['f_neck_down_L'][1])*f_ratio
        left,right = cut_by_y(s_pf.reverse_transform_y(f_neck_bot_y),self.side_body.outline)
        self.data.append(s_pf.transform_str(*left))
        #S脖子L_top
        f_neck_top_y = f_pf.transorm_y(self.front_body.features['f_neck_up_L'][1])*f_ratio
        left, right = cut_by_y(s_pf.reverse_transform_y(f_neck_top_y), self.side_body.outline)
        self.data.append(s_pf.transform_str(*left))

        self.data.append(angle(self.side_body.features['s_neck_up_L'],self.side_body.features['s_neck_up_R']))#脖子角度
        # self.data.append(distance(self.front_body.features['f_shoulder_L'],self.front_body.features['f_wrist_left_L']))#左臂长L
        # self.data.append(distance(self.front_body.features['f_shoulder_R'], self.front_body.features['f_wrist_right_R']))#右臂长R
        self.data.append(distance(self.front_body.features['f_shoulder_L'], self.front_body.features['f_wrist_left_L']))  # 左臂长L
        self.data.append(distance(self.front_body.features['f_shoulder_R'], self.front_body.features['f_wrist_right_R']))#右臂长R
        self.data.append(s_pf.transform_str(*self.side_body.features['s_xiong_R'])) #S胸R
        self.data.append(f_pf.transform_str(*self.front_body.features['f_wrist_left_L']))  # 手腕L
        self.data.append(f_pf.transform_str(*self.front_body.features['f_wrist_right_R']))  # 手腕R

        self.data.append(self.front_body.bottom_y-self.front_body.foot_y)#真实脚高F
        self.data.append(self.side_body.bottom_y - self.side_body.foot_y)  # 真实脚高S
        self.data.append(f_height)# 像素身高F
        self.data.append(s_height)  # 像素身高S
        print(len(self.data))
        return self.data

    def export_features(self):
        features={}
        for k,v in self._map.items():
            body=self.front_body
            if k.startswith('s_'):
                body=self.side_body
            features['%s_x'%v],features['%s_y'%v]=body.features[k]


        features['top_x'],features['top_y']=self.front_body.top_head_point  #'头顶x坐标',
        features['hand_r_x'], features['hand_r_y'] = self.front_body.right_finger
        # self._map['f_wrist_right_R']='hand_r' # '右边手尖x',
        features['perineum_x'], features['perineum_y'] = self.front_body.huiyin_point
        features['hand_l_x'], features['hand_l_y'] = self.front_body.left_finger
        # self._map['f_wrist_left_L']='hand_l' # '左边手尖x',
        features['top_s_x'], features['top_s_y'] = self.side_body.top_head_point

        # self._map['']='bust_s' # '侧面胸高交点x坐标',


        # self._map['']='neck_angle' # '侧面脖子角度',
        # features['neck_angle']=0.3
        features['neck_angle'] = angle(self.side_body.features['s_neck_up_L'], self.side_body.features['s_neck_up_R'])
        # features['foot_line']=self.front_body.bottom_y - self.front_body.foot_y
        # features['foot_line_s'] = self.side_body.bottom_y - self.side_body.foot_y
        # features['foot_line'] = self.front_body.foot_y + 10
        # features['foot_line_s'] = self.side_body.foot_y + 10

        fbody=self.front_body
        sbody=self.side_body
        left_foot,right_foot=None,None
        # print(fbody.features)
        if 'left_foot' in fbody.features:
            left_foot=fbody.features['left_foot']
        if 'right_foot' in fbody.features:
            right_foot=fbody.features['right_foot']
        # print(left_foot,right_foot)
        left_foot_line,right_foot_line=None,None
        if left_foot:
            h=fbody._max_y-left_foot[1]
            if 50<=h<=150:
                left_foot_line=h
        if right_foot:
            h=fbody._max_y-right_foot[1]
            if 50 <= h <= 150:
                right_foot_line=h
        if left_foot_line or right_foot_line:
            if not left_foot_line:
                left_foot_line=150
            if not right_foot_line:
                right_foot_line=150
            foot_line=min(left_foot_line,right_foot_line)
            # print(foot_line)
        else:
            foot_line=100
        # print(foot_line)
        f_h=fbody._max_y-fbody._min_y
        s_h=sbody._max_y-sbody._min_y

        foot_line_s=int(foot_line*(s_h/f_h))

        foot_line=fbody.img_h-(fbody._max_y-foot_line)
        foot_line_s=sbody.img_h-(sbody._max_y-foot_line_s)
        features['foot_line'] = foot_line
        features['foot_line_s'] = foot_line_s

        features['deflection'], features['deflection_s']=0,0
        return features

if __name__ == '__main__':
    # f=FeatureTan(None,None)
    # f.write_file('test_FL.txt')
    lines = FeatureTan.template.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    for i,line in enumerate(lines):
        print(i, line)

