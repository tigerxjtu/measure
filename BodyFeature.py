import numpy as np
from BodyClient import body_client
from utils import distance



def round_int(x):
    return int(round(x,0))

def min_feature(outline,lower_pct,upper_pct,top_y,bottom_y):
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
    return result[ind,0],result[ind,1],result[ind,2] # x_left,x_right, y

def on_line(pt1, pt2, angle):
    x1,y1 = pt1
    x2,y2 = pt2
    if x1==x2:
        return y1==y2
    dx = x2 - x1
    y = round_int(y1 - angle * dx)
    return abs(y-y2)<=1

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

def max_feature(outline,lower_pct,upper_pct,top_y,bottom_y):
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
    return int(result[ind,0]),int(result[ind,1]),int(result[ind,2]) # x_left,x_right, y

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

def min_distance_angle(outline,pt,angle):
    pts = filter(lambda x: on_line(x, pt, angle), outline)
    distances = [(p, distance(pt, p)) for p in pts]
    if distances:
        min_distance = min(distances, key=lambda x: x[1])
        return min_distance
    return None


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







