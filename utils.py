import numpy as np

def get_file_content(self, filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def expand_rect(self, x, y, w, h, max_w, max_h, ratio=0.05):
    left = int(max(x - ratio * w, 0))
    top = int(max(y - ratio * h, 0))
    width = int(min((1 + 2 * ratio) * w, max_w - left))
    height = int(min((1 + 2 * ratio) * h, max_h - top))
    return left, top, width, height

def distance(p1,p2):
    x1,y1=p1
    x2,y2=p2
    return np.sqrt((x2-x1)**2+(y2-y1)**2)

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

if __name__ == '__main__':
    p1=(0,2)
    p2=(4,4)
    p=(2,3)
    print(is_one_line(p1,p2,p))