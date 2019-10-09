import numpy as np

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def expand_rect( x, y, w, h, max_w, max_h, ratio=0.05):
    left = int(max(x - ratio * w, 0))
    top = int(max(y - ratio * h, 0))
    width = int(min((1 + 2 * ratio) * w, max_w - left))
    height = int(min((1 + 2 * ratio) * h, max_h - top))
    return left, top, width, height

#两点间距离
def distance(p1,p2):
    x1,y1=p1
    x2,y2=p2
    return np.sqrt((x2-x1)**2+(y2-y1)**2)

#两点连线跟水平的夹角
def angle(p1,p2):
    x1, y1 = p1
    x2, y2 = p2
    return -(y2-y1)/(x2-x1)

#判断三点是否共线
def is_one_line(left_point,right_point,cur_point):
    left_x, left_y = left_point
    right_x, right_y = right_point
    cur_x,cur_y = cur_point
    if left_x==right_x:
        return cur_x==left_x
    dx=right_x-left_x
    dy=right_y-left_y
    y_pos=y_pos=int(round((cur_x-left_x)*dy/dx+left_y,0))
    return cur_y==int(y_pos)

# (x,y)
def min_point(points):
    point = min(points,key=lambda x:x[1])
    return point

#轮廓上根据y找到左右两边的点，左边最左，右边最右
def cut_by_y(y,outline):
    y=int(round(y,0))
    points = filter(lambda x: x[1] == y, outline)
    points = list(points)
    left = min(points,key=lambda x:x[0])
    right = max(points,key=lambda x:x[0])
    return left,right

#两点连线上根据y0找到交点的x
def x_inersect_y(pt_up, pt_down, y0):
    x1,y1 = pt_up
    x2,y2 = pt_down
    x0 = (x2-x1)*(y0-y1)/(y2-y1)+x1
    return x0


if __name__ == '__main__':
    p1=(0,2)
    p2=(4,4)
    p=(2,3)
    print(is_one_line(p1,p2,p))