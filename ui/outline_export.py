from ui.PointTransformer import PtTransformer

DEBUG = False

class Curves(object):

    def __init__(self, start_point, up_curv=None):
        self.start_point = start_point
        self.curves = [start_point]
        # self.up_curv = up_curv
        # self.down_curves = []
        self.last_point = start_point
        self.back_tracing = False

    def reverse(self):
        self.start_point,self.last_point = self.last_point, self.start_point
        self.curves = self.curves[::-1]
        return self

    def add_point(self, point):
        self.curves.append(point)
        self.last_point = point

    def add_points(self,points):
        if not points:
            return
        self.curves.extend(points)
        self.last_point = points[-1]

    def is_connected(self,right_curve):
        if self.last_point[0]==right_curve.start_point[0] and self.last_point[1]==right_curve.start_point[1]:
            return True
        return False

    def is_near(self,right_curve):
        if abs(self.last_point[0]-right_curve.start_point[0])<=1 and abs(self.last_point[1]-right_curve.start_point[1])<=1:
            return True
        return False

    def is_next(self,right_curve):
        if abs(self.last_point[0] - right_curve.start_point[0]) <= 1:
            return True
        return False



class OutlineTransformer(object):

    def __init__(self, outline_points, top_point):
        self.top_point = top_point
        self.outline = outline_points
        self.cross_curves = []
        # print(len(self.outline))

    def is_near(self,pt,curve):
        last_pt=curve.last_point
        if abs(last_pt[0]-pt[0])<=1:
            return True
        return False

    def process_first_row(self,points):
        left_curv=Curves(self.top_point)
        curv=Curves(self.top_point)
        leaf_curves = [left_curv,curv]
        cur_point = self.top_point
        prev_point = cur_point
        for p in points[1:]:
            if p[0] == prev_point[0]+1:
                curv.add_point(p)
            else:
                curv=Curves(p)
                leaf_curves.append(curv)
            prev_point = p
        return leaf_curves

    def merge_points(self,points,curve):
        last_point = curve.last_point
        p_head=points[0]
        p_tail=points[-1]
        if p_head[0]==last_point[0]:
            curve.add_points(points)
            return True
        else:
            if self.is_near(p_tail,curve):
                curve.add_points(points[::-1])
                return True
            else:
                if self.is_near(p_head,curve):
                    curve.add_points(points)
                    return True
                return False


    def merge_curve(self,left_curve, right_curve):
        if left_curve.is_connected(right_curve):
            left_curve.add_points(right_curve.curves[1:])
        else:
            if left_curve.is_next(right_curve):
                left_curve.add_points(right_curve.curves)
            else:
                left_curve.add_points(right_curve.curves[::-1])
        return left_curve

    def process_row(self, points, leaf_curves):
        temp_points = []
        prev_point = points[0]
        cur_y = prev_point[1]
        curves = []
        cur_curve = None
        next_curve = None
        for p in points[1:]:
            temp_points.append(prev_point)
            if p[0] == prev_point[0] + 1:
                # temp_points.append(p)
                prev_point = p
                continue
            if not cur_curve:
                cur_curve=self.get_next_curve(leaf_curves,curves,cur_y)
                if not cur_curve and temp_points:
                    left_curve = Curves(temp_points[0])
                    left_curve.back_tracing = True
                    curves.append(left_curve)
                    right_curve = Curves(temp_points[0])
                    right_curve.add_points(temp_points[1:])
                    curves.append(right_curve)
                    temp_points.clear()
                    prev_point = p
                    continue
            # if temp_points:
            while cur_curve:
                if self.merge_points(temp_points,cur_curve):
                    temp_points.clear()
                    #不合并
                    curves.append(cur_curve)
                    cur_curve =  self.get_next_curve(leaf_curves,curves,cur_y)
                    break
                    '''
                    last_pt = prev_point
                    while len(leaf_curves)>0:
                        next_curve = self.get_next_curve(leaf_curves,curves,cur_y)
                        if self.is_near(last_pt,next_curve) or cur_curve.is_connected(next_curve):
                            cur_curve = self.merge_curve(cur_curve,next_curve)
                            last_pt = cur_curve.last_point
                        else:
                            curves.append(cur_curve)
                            cur_curve = next_curve
                            break
                    '''
                    # else:
                    #     # print('may lose curve')
                    #     curves.append(cur_curve)
                    #     cur_curve = None
                else:
                    '''
                    merged = False
                    if len(curves)>0:
                        back_curve=curves[-1]
                        if self.is_near(temp_points[0],back_curve):
                            self.merge_points(temp_points,back_curve)
                            merged = True
                    if not merged:
                        #这里是重要的特征点，后续要进行提取
                        left_curve = Curves(temp_points[0])
                        left_curve.back_tracing = True
                        curves.append(left_curve)
                        right_curve = Curves(temp_points[0])
                        right_curve.add_points(temp_points[1:])
                        curves.append(right_curve)
                    temp_points.clear()
                    '''
                    if cur_curve.last_point[0] < temp_points[0][0]:  # left_sice
                        curves.append(cur_curve)
                        cur_curve = self.get_next_curve(leaf_curves,curves,cur_y)
                        continue
                    # 这里是重要的特征点，后续要进行提取
                    left_curve = Curves(temp_points[0])
                    left_curve.back_tracing = True
                    curves.append(left_curve)
                    right_curve = Curves(temp_points[0])
                    right_curve.add_points(temp_points[1:])
                    curves.append(right_curve)
                    temp_points.clear()
                    break
            prev_point = p
        #处理剩余的点
        temp_points.append(prev_point)
        if not cur_curve:
            cur_curve = self.get_next_curve(leaf_curves, curves, cur_y)
        while cur_curve:
            if self.merge_points(temp_points, cur_curve):
                last_pt = temp_points[-1]
                temp_points.clear()
                '''
                while len(leaf_curves) > 0:
                    next_curve = leaf_curves.pop(0)
                    if self.is_near(prev_point, next_curve) or cur_curve.is_connected(next_curve):
                        cur_curve = self.merge_curve(cur_curve, next_curve)
                        last_pt = cur_curve.last_point
                    else:
                        # print('may have problem')
                        curves.append(cur_curve)
                        cur_curve = next_curve
                        break
                '''
                # # else:
                # #     # print('may have problem')
                #     curves.append(cur_curve)
                curves.append(cur_curve)
                cur_curve = None

            else:
                '''
                merged = False
                if len(curves) > 0:
                    back_curve = curves[-1]
                    if self.is_near(temp_points[0], back_curve):
                        self.merge_points(temp_points, back_curve)
                        merged = True
                if not merged:
                    inserted= False
                    if cur_curve and cur_curve.last_point[0]<temp_points[0][0]: #left_sice
                        curves.append(cur_curve)
                        inserted = True
                    # 这里是重要的特征点，后续要进行提取
                    left_curve = Curves(temp_points[0])
                    left_curve.back_tracing = True
                    curves.append(left_curve)
                    right_curve = Curves(temp_points[0])
                    right_curve.add_points(temp_points[1:])
                    curves.append(right_curve)
                    if cur_curve and not inserted:
                        curves.append(cur_curve)
                temp_points.clear()
                '''
                if cur_curve.last_point[0] < temp_points[0][0]:  # left_sice
                    curves.append(cur_curve)
                    cur_curve = self.get_next_curve(leaf_curves, curves, cur_y)
                    continue
                break
        if temp_points:
            while cur_curve and  cur_curve.last_point[0] < temp_points[0][0]:  # left_sice
                curves.append(cur_curve)
                cur_curve = self.get_next_curve(leaf_curves, curves, cur_y)
            # 这里是重要的特征点，后续要进行提取
            left_curve = Curves(temp_points[0])
            left_curve.back_tracing = True
            curves.append(left_curve)
            right_curve = Curves(temp_points[0])
            right_curve.add_points(temp_points[1:])
            curves.append(right_curve)
            temp_points.clear()
        if cur_curve:
            curves.append(cur_curve)
            '''
            self.print_summary(curves)
            last_pt = cur_curve.last_point
            p_head = temp_points[0]
            if p_head[1]-last_pt[1]<8: #暂时先合并
                cur_curve.add_points(temp_points)
                curves.append(cur_curve)
            else:
                raise Exception(
                    'last points {} not merged: {},{}'.format(temp_points, cur_curve.start_point, cur_curve.last_point))
            '''
        if len(leaf_curves)>0:
            # print('warn-------------')
            # self.print_summary(curves)
            # raise Exception('{} leaf curves exists: {}, {}'.format(len(leaf_curves),leaf_curves[0].last_point,prev_point))
            if DEBUG:
                print('warn: {} leaf curves exists: {}, {}'.format(len(leaf_curves),leaf_curves[0].last_point,prev_point))
            curves.extend(leaf_curves)
            leaf_curves.clear()
        self.print_summary(curves)
        # curves = self.check_curves(curves,cur_y)
        # self.print_summary(curves)
        return curves

    def get_next_curve(self, leaf_curves, curves, cur_y):
        if len(leaf_curves) < 1:
            # raise Exception('no leaf_curve left')
            return None
        cur_curve = leaf_curves.pop(0)

        while cur_curve.last_point[1] < cur_y-1:
            curves.append(cur_curve)
            if len(leaf_curves) > 0:
                cur_curve = leaf_curves.pop(0)
            else:
                # raise Exception('no leaf_curve left')
                return None
        #上一轮刚加入的点进行合并检查处理
        if cur_curve and cur_curve.back_tracing and len(cur_curve.curves)==1:
            cur_curve.back_tracing = False
            if curves:
                back_curve = curves[-1]
                if self.is_near(cur_curve.start_point,back_curve): #合并
                    next_curve=leaf_curves.pop(0)
                    if cur_curve.is_connected(next_curve):
                        back_curve.add_points(next_curve.curves)
                        cur_curve = curves.pop()
                    else:
                        back_curve.add_point(cur_curve.start_point)
                        cur_curve=next_curve
        return cur_curve

    def check_curves(self,curves,cur_y):
        prev_curv = curves[0]
        temp_curves = []
        merging = False
        for curv in curves[1:]:
            if prev_curv.last_point[1]<cur_y or merging:
                if prev_curv.is_connected(curv):
                    prev_curv.add_points(curv.curves[1:])
                    merging = True
                else:
                    if prev_curv.is_near(curv):
                        prev_curv.add_points(curv.curves)
                        merging = True
                    else:
                        if prev_curv.last_point[1]<cur_y:
                            raise Exception('curv not right: {},{}'.format(prev_curv.start_point,prev_curv.last_point))
                        else:
                            # temp_curves.append(prev_curv)
                            merging = False
                continue

            else:
                temp_curves.append(prev_curv)
                prev_curv = curv
                merging = False

        if not prev_curv.is_connected(curv):
            temp_curves.append(curv)
        return temp_curves

    def cnt_curves(self,curves):
        cnt = 0
        for curv in curves:
            cnt += len(curv.curves)
        return cnt

    def print_summary(self,curves):
        if not DEBUG:
            return
        cnt = self.cnt_curves(curves)
        if cnt < self.pts:
            print('warn: {} < {} -----------------------------------------------------------------------------------------------'.format(cnt,self.pts))
        print(cnt,self.pts,'--------------------------------')
        for i,curve in enumerate(curves):
            print(i, len(curve.curves), curve.start_point,curve.last_point)

    def scan(self):
        cur_y = self.top_point[1]
        leaf_curves = []
        temp_points = []
        first_line = True
        self.pts=0
        for p in self.outline:
            if first_line and p[1] == cur_y:
                temp_points.append(p)
                continue
            if first_line and p[1] > cur_y:
                first_line = False
                self.pts += len(temp_points)
                leaf_curves = self.process_first_row(temp_points)
                temp_points.clear()
                temp_points.append(p)
                cur_y += 1
                continue

            if p[1]==cur_y:
                temp_points.append(p)
                continue
            else:
                self.pts += len(temp_points)
                leaf_curves = self.process_row(temp_points,leaf_curves)
                temp_points.clear()
                temp_points.append(p)
                cur_y += 1
        self.pts += len(temp_points)
        leaf_curves = self.process_row(temp_points, leaf_curves)
        # cur_curve=leaf_curves.pop(0)
        # while len(leaf_curves) > 0:
        #     next_curve = leaf_curves.pop(0)
        #     if self.is_near(cur_curve.last_point, next_curve):
        #         cur_curve = self.merge_curve(cur_curve, next_curve)

        return leaf_curves

    def is_same(self,pt1,pt2):
        return pt1[0]==pt2[0] and pt1[1]==pt2[1]

    def is_neighbor(self,pt1,pt2):
        return abs(pt1[0]-pt2[0])<=1 and abs(pt1[1]-pt2[1])<=1

    def comine_vetex(self, curves):
        if not curves:
            return curves,False
        temp_curves = []
        flag = False
        prev_curv = curves[0]
        for curv in curves[1:]:
            if self.is_same(prev_curv.start_point,curv.start_point):
                prev_curv.reverse()
                prev_curv.add_points(curv.curves[1:])
                flag = True
            else:
                temp_curves.append(prev_curv)
                prev_curv = curv
        temp_curves.append(prev_curv)
        return temp_curves,flag

    def filter_small_curves(self,curves, thresh=3):
        cs = filter(lambda x:len(x.curves)>thresh,curves )
        return [curv for curv in cs]

    def connect_vetex(self,curves):
        if not curves:
            return curves
        temp_curves = []
        prev_curv = curves[0]
        for curv in curves[1:]:
            if self.is_neighbor(prev_curv.last_point,curv.start_point):
                prev_curv.add_points(curv.curves)
            else:
                temp_curves.append(prev_curv)
                prev_curv = curv
        temp_curves.append(prev_curv)
        return temp_curves

    def connect_tail(self,curves):
        if not curves:
            return curves
        temp_curves = []
        prev_curv = curves[0]
        for curv in curves[1:]:
            if self.is_neighbor(prev_curv.last_point,curv.last_point):
                prev_curv.add_points(curv.curves[::-1])
            else:
                temp_curves.append(prev_curv)
                prev_curv = curv
        temp_curves.append(prev_curv)
        return temp_curves

    def dis(self,pt1,pt2):
        return abs(pt1[0]-pt2[0]) + abs(pt1[1]-pt2[1])

    def distance(self,left_start,left_last,right_start,right_last):
        ds=[(left_last,right_start),(left_last,right_last)]
        min_index=0
        min_dis=self.dis(ds[0][0],ds[0][1])
        for i,pair in enumerate(ds[1:]):
            dis = self.dis(pair[0],pair[1])
            if dis<min_dis:
                min_index = i+1
                min_dis = dis
        return min_index,min_dis

    def prob_merge(self,left_curv,right_curv,thresh=50):
        index,dis = self.distance(left_curv.start_point,left_curv.last_point,right_curv.start_point,right_curv.last_point)
        if dis<=thresh:
            return True,index
        return False,None

    def force_connect(self,curves):
        if not curves:
            return []
        if len(curves)==1:
            points = curves[0].curves
            points.pop(0)
            return points[::-1]
        prev_curv = curves[0]
        # first = True
        for curv in curves[1:]:
            flag,index = self.prob_merge(prev_curv,curv)
            # index += 2
            if flag:
                # if index<2:
                #     raise Exception('Cannot merge to one curve')
                if index==0:
                    prev_curv.add_points(curv.curves)
                else:
                    prev_curv.add_points(curv.curves[::-1])
                    # raise Exception('Cannot merge to one curve')
                # first = False
            else:
                raise Exception('Cannot merge to one curve')
        self.print_summary([prev_curv])
        points = prev_curv.curves
        points.pop(0)
        return points[::-1]

    def down_order_points(self,points):
        if not points:
            return points
        start,end = points[0],points[-1]
        if start[1]>end[1]:
            return points[::-1]
        return points

    def to_one_curve(self,curves,reverse=False):
        if not curves:
            return []
        curve = max(curves,key=lambda curve: len(curve.curves))
        points = curve.curves
        points.pop(0)
        return self.down_order_points(points)

    def merge_curves(self,curves):
        new_curves, flag = self.comine_vetex(curves)
        while flag:
            new_curves, flag = self.comine_vetex(new_curves)
        self.print_summary(new_curves)
        new_curves = self.connect_vetex(new_curves)
        self.print_summary(new_curves)
        new_curves = self.connect_tail(new_curves)
        self.print_summary(new_curves)
        new_curves = self.filter_small_curves(new_curves)
        return new_curves




class OutlineTan(object):

    def __init__(self, front_body, side_body):
        self.front_body = front_body
        self.side_body = side_body

    def export_front(self,file_path):
        outline_transformer = OutlineTransformer(self.front_body.outline, self.front_body.top_head_point)
        curves = outline_transformer.scan()
        curves = outline_transformer.merge_curves(curves)
        curve_points = outline_transformer.force_connect(curves)
        if self.front_body.bottom_y and self.front_body.center_x:
            cent_x = self.front_body.center_x
            bottom_y = self.front_body.bottom_y
        else:
            cent_x = (self.front_body._min_x+self.front_body._max_x)//2
            bottom_y = self.front_body._max_y
        pf = PtTransformer(cent_x, bottom_y)
        s_head = '{},{},{}\n'.format(len(curve_points),cent_x,bottom_y)
        with open(file_path, 'w') as fp:
            fp.write(s_head)
            for pt in curve_points:
                fp.write(pf.transform_str(*pt)+'\n')

    def export_side(self,file_path):
        outline_transformer = OutlineTransformer(self.side_body.outline, self.side_body.top_head_point)
        curves = outline_transformer.scan()
        curves = outline_transformer.merge_curves(curves)
        curve_points = outline_transformer.force_connect(curves)
        if self.side_body.bottom_y and self.side_body.center_x:
            cent_x = self.side_body.center_x
            bottom_y = self.side_body.bottom_y
        else:
            cent_x = (self.side_body._min_x+self.side_body._max_x)//2
            bottom_y = self.side_body._max_y
        pf = PtTransformer(cent_x, bottom_y)
        s_head = '{},{},{}\n'.format(len(curve_points),cent_x,bottom_y)
        with open(file_path, 'w') as fp:
            fp.write(s_head)
            for pt in curve_points:
                fp.write(pf.transform_str(*pt) + '\n')




