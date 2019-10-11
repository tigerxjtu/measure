import numpy as np
from BodyClient import body_client
from utils import distance
from ui.outline_export import OutlineTransformer


#对x按四舍五入取整
def round_int(x):
    return int(round(x,0))

#按照（lower_y,upper_y）范围内在轮廓线上按水平方向找最短距离的交点集
def min_feature_range(outline,lower_y,upper_y):
    X = np.array([p[0] for p in outline])
    Y = np.array([p[1] for p in outline])

    target = np.where(Y >= lower_y)
    Y = Y[target]
    X = X[target]

    target = np.where(Y <= upper_y)
    Y = Y[target]
    X = X[target]

    result = np.zeros((upper_y - lower_y + 1, 3), dtype=np.int)
    distances = np.zeros((upper_y - lower_y + 1), dtype=np.int)

    i = 0
    for y in range(lower_y, upper_y + 1):
        result[i, 2] = y
        index = np.where(Y == y)
        x = X[index]
        result[i, 0] = np.min(x)
        result[i, 1] = np.max(x)
        distances[i] = result[i, 1] - result[i, 0]
        i += 1
    index = np.where(distances > 0)
    result = result[index]
    distances = distances[index]
    ind = np.argmin(distances)
    return result[ind, 0], result[ind, 1], result[ind, 2]  # x_left,x_right, y

#按照（lower_pct,upper_pct,top_y,bottom_y）范围内在轮廓线上按水平方向找最短距离的交点集
def min_feature(outline,lower_pct,upper_pct,top_y,bottom_y):
    Y = np.array([p[1] for p in outline])
    if not top_y:
        bottom_y = np.max(Y)
        top_y = np.min(Y)
    h = bottom_y - top_y
    lower_y = round_int(top_y + lower_pct * h)
    upper_y = round_int(top_y + upper_pct * h)
    return min_feature_range(outline,lower_y,upper_y) # x_left,x_right, y

#判断两点连线和水平夹角是否为angle
def on_line(pt1, pt2, angle):
    x1,y1 = pt1
    x2,y2 = pt2
    if x1==x2:
        return y1==y2
    dx = x2 - x1
    y = round_int(y1 - angle * dx)
    return abs(y-y2)<=1

#根据mean_x在点集points内找到左边最近和右边最近的点
def get_two_points(points,mean_x):
    cut_left, cut_right = None, None
    for p in points:
        # print(p)
        if p[0] <= mean_x:
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

#按照（lower_y,upper_y）范围内在轮廓线上按水平方向找最长距离的交点集
def max_feature_range(outline,lower_y,upper_y):
    X = np.array([p[0] for p in outline])
    Y = np.array([p[1] for p in outline])

    target = np.where(Y >= lower_y)
    Y = Y[target]
    X = X[target]

    target = np.where(Y <= upper_y)
    Y = Y[target]
    X = X[target]

    result = np.zeros((upper_y - lower_y + 1, 3), dtype=np.int)
    distances = np.zeros((upper_y - lower_y + 1), dtype=np.int)

    i = 0
    for y in range(lower_y, upper_y + 1):
        result[i, 2] = y
        index = np.where(Y == y)
        x = X[index]
        result[i, 0] = np.min(x)
        result[i, 1] = np.max(x)
        distances[i] = result[i, 1] - result[i, 0]
        i += 1
    index = np.where(distances > 0)
    result = result[index]
    distances = distances[index]
    ind = np.argmax(distances)
    return int(result[ind, 0]), int(result[ind, 1]), int(result[ind, 2])  # x_left,x_right, y


#按照（lower_pct,upper_pct,top_y,bottom_y）范围内在轮廓线上按水平方向找最长距离的交点集
def max_feature(outline,lower_pct,upper_pct,top_y,bottom_y):
    Y = np.array([p[1] for p in outline])
    if not top_y:
        bottom_y = np.max(Y)
        top_y = np.min(Y)
    h = bottom_y - top_y
    lower_y = round_int(top_y + lower_pct * h)
    upper_y = round_int(top_y + upper_pct * h)
    return max_feature_range(outline, lower_y, upper_y)  # x_left,x_right, y


#按照（lower_pct,upper_pct,top_y,bottom_y）范围内在轮廓线上找angle角度直线交点的最短距离的距离和交点集
def min_angle_feature(outline,lower_pct,upper_pct,top_y,bottom_y,angle=0.3):
    X = np.array([p[0] for p in outline])
    Y = np.array([p[1] for p in outline])
    if not top_y:
        bottom_y = np.max(Y)
        top_y = np.min(Y)
    h = bottom_y - top_y
    lower_y = round_int(top_y + lower_pct * h)
    upper_y = round_int(top_y + upper_pct * h)

    target = np.where(Y >= lower_y)
    Y = Y[target]
    X = X[target]

    target = np.where(Y <= upper_y)
    Y = Y[target]
    X = X[target]

    mean_x = int(np.mean(X))
    mean_y = int((lower_y+upper_y)/2)
    candidates = []
    points = zip(X,Y)
    for index in range(mean_y-lower_y):
        y = mean_y+index
        pts = filter(lambda x: on_line(x,(mean_x,y),angle),points)
        left,right = get_two_points(pts,mean_x)
        if left and right:
            candidates.append((left,right))

    for index in range(mean_y - lower_y):
        y = mean_y - index
        pts = filter(lambda x: on_line(x, (mean_x, y), angle),points)
        # pts = [pt for pt in pts]
        left, right = get_two_points(pts, mean_x)
        if left and right:
            candidates.append((left, right))

    distances = [(p1,p2,distance(p1,p2)) for p1,p2 in candidates]
    if distances:
        min_distance = min(distances, key=lambda x: x[2])
        return min_distance
    return None

#按照角度方向轮廓线上交点之间的最短距离
def min_distance_angle(outline,pt,angle):
    pts = filter(lambda x: on_line(x, pt, angle), outline)
    distances = [(p, distance(pt, p)) for p in pts]
    if distances:
        min_distance = min(distances, key=lambda x: x[1])
        return min_distance
    return None

def add_distance(distances, row ,x0, y):
    try:
        if len(row) < 2:
            return
        x_left, x_right = None, None
        if row[0]>x0 or  row[-1]<x0:
            x0=int(np.mean(row))
        for x1 in row:
            if x1 < x0:
                x_left = x1 if x_left is None else max(x1,x_left)
            else:
                x_right = x1 if x_right is None else min(x1,x_right)
        distances.append(x_right-x_left)
    except Exception as e:
        print(x_left,x_right,y, e)
        # raise e

#（y_up，y_down）之间在轮廓线上水平方向的距离集合
def get_outline_distribute(outline, y_up, y_down, x0):
    distances = []
    prev_y = y_up
    row = []
    for pt in outline:
        x1,y1=pt
        if y1<y_up:
            continue
        if y1>y_down:
            break
        if y1==prev_y:
            row.append(x1)
        else:
            add_distance(distances,row,x0,prev_y)
            prev_y = y1
            row.clear()
            row.append(x1)
    add_distance(distances, row, x0, prev_y)
    return distances



#根据y0，在轮廓上找到下方最近的点，范围在（）
def min_y_pt(outline, x_low, x_high, y0):
    pts = filter(lambda x: x[0]>=x_low and x[0]<=x_high and x[1]-y0>20, outline)
    pts = [p for p in pts]
    point = min(pts, key=lambda x: x[1])
    return point

class BodyFeature(object):

    def __init__(self):
        self.front_ponits = {}
        self.front_outline = []
        self.fornt_rect = None

        self.side_ponits = {}
        self.side_outline = []
        self.side_rect = None

    def process_front(self,front_file):
        self.front_ponits,self.front_outline,self.front_rect = body_client.process_body(front_file)


    def process_side(self,side_file):
        self.side_ponits, self.side_outline,self.side_rect = body_client.process_body(side_file)

    def front_height(self):
        return self.fornt_rect[3]

    def side_height(self):
        return self.side_rect[3]

    def save(self):
        pass

    def load(self):
        pass

def is_neighbor(p1,p2, threshold=20):
    x1, y1 = p1
    x2, y2 = p2
    dis=abs(x1-x2)+abs(y1-y2)
    return dis<=threshold

def angle(center,left,right):
    a=distance(left,center)
    b=distance(center,right)
    c=distance(left,right)
    ang=c/(a+b)
    return ang

def angle_point(points,delta=5):
    size=len(points)
    angles=[1 for _ in range(size)]
    for i in range(delta+20,size-delta):
        angles[i]=angle(points[i],points[i-delta],points[i+delta])
    index=np.argmin(angles)
    return index,points[index]

def part_bound(max_y,min_y,lower,upper):
    h = max_y - min_y
    lower_y = min_y + lower * h
    upper_y = min_y + upper * h
    return int(lower_y), int(upper_y)

#shoulder: 0.17~0.22
def shoulder_bound(max_y,min_y):
    lower, upper = 0.17, 0.22
    return part_bound(max_y, min_y, lower, upper)

def shoulder_markers(points):
    X = np.array([p[0] for p in points])
    Y = np.array([p[1] for p in points])
    max_y = np.max(Y)
    min_y = np.min(Y)
    lower_y, upper_y = shoulder_bound(max_y, min_y)

    shoulder = np.where(Y >= lower_y)
    Y = Y[shoulder]
    X = X[shoulder]

    shoulder = np.where(Y <= upper_y)
    Y = Y[shoulder]
    X = X[shoulder]

    points=zip(X,Y)
    part1=[]
    part2=[]
    for p in points:
        if part1:
            last=part1[-1]
            if is_neighbor(last,p):
                part1.append(p)
            else:
                if part2:
                    if not is_neighbor(part2[-1],p):
                        print(p,'is invalid', last)
                        continue
                part2.append(p)
        else:
            part1.append(p)
    print(part1)
    print(part2)
    _,point1=angle_point(part1)
    _,point2=angle_point(part2)
    print(point1,point2)
    return point1,point2

def pt_in_range(pt, start_point, end_point, delta=1):
    start_x,start_y = start_point
    end_x,end_y = end_point
    start_y -= delta #应对错位
    x,y = pt
    if (start_x-x>=0 and x-end_x>=0) or (start_x-x<0 and x-end_x<0):
        if (start_y - y >= 0 and y - end_y >= 0) or (start_y - y < 0 and y - end_y < 0):
            return True
    return False

#start_point： left most/ max_y , end_point: right_most/min_y
def range_outline(outline, start_point, end_point):
    points = filter(lambda x: pt_in_range(x,start_point,end_point), outline)
    points = list(points)
    if not points:
        return []
    outline_transformer = OutlineTransformer(points,points[0])
    curves = outline_transformer.scan()
    curves = outline_transformer.merge_curves(curves)
    curve_points = outline_transformer.to_one_curve(curves)
    return curve_points

def calc_delta(pt1,pt2):
    x1,y1=pt1
    x2,y2=pt2
    if x1==x2:
        return None
    return (y2-y1)/(x2-x1)

def outline_delta(points, delta=3):
    result = []
    if not points:
        return result
    prev_pt=points[0]
    for i,pt in enumerate(points):
        if i<delta:
            result.append(0)
            continue
        result.append(calc_delta(pt,prev_pt))
        prev_pt = points[i-delta+1]
    return result

def speed_delta(points, delta=3):
    print('points:',points)
    speed = outline_delta(points,delta)
    print('speed:',speed)
    result = [0]
    prev=speed[0]
    for p in speed[1:]:
        try:
            result.append(p - prev)
        except:
            result.append(0)
        prev=p
    print('speed2:', result)
    return result










