import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import filters
from ui.outline_export import OutlineTransformer
import json
import os
from Config import config


class FeatureAdjust(object):

    def __init__(self, front_body, side_body):
        self.front_body = front_body
        self.side_body = side_body
        self.adjust_features = {}

    def _out_file_path(self):
        if self.front_body.folder:
            base_path = os.path.join(config.result_dir, self.front_body.folder)
        else:
            base_path = config.result_dir
        return os.path.join(base_path,'%s.json'%self.front_body.body_id)

    def adjust(self):
        self.adjust_feature_yao()
        self.adjust_feature_tun()
        file = self._out_file_path()
        with open(file, 'w') as fp:
            json.dump(self.adjust_features, fp)

    def adjust_feature_yao(self):
        f_yao_L, f_yao_R = self.front_body.auto_features['yao_L'], self.front_body.auto_features['yao_R']
        s_yao_L, s_yao_R = self.side_body.auto_features['yao_L'], self.side_body.auto_features['yao_R']
        f_img, s_img = self._read_img()
        f_img_cut_L, f_rect_cut_L = self._cut_img(f_img, f_yao_L)
        f_img_cut_R, f_rect_cut_R = self._cut_img(f_img, f_yao_R)
        s_img_cut_L, s_rect_cut_L = self._cut_img(s_img, s_yao_L)
        s_img_cut_R, s_rect_cut_R = self._cut_img(s_img, s_yao_R)
        self.adjust_features['f_yao_L'] = self.adjust_feature_x(f_img_cut_L, f_rect_cut_L)
        self.adjust_features['f_yao_R'] = self.adjust_feature_x(f_img_cut_R, f_rect_cut_R)
        self.adjust_features['s_yao_L'] = self.adjust_feature_x(s_img_cut_L, s_rect_cut_L)
        self.adjust_features['s_yao_R'] = self.adjust_feature_x(s_img_cut_R, s_rect_cut_R)

    def adjust_feature_tun(self):
        f_tun_L, f_tun_R = self.front_body.auto_features['tun_L'], self.front_body.auto_features['tun_R']
        s_tun_L, s_tun_R = self.side_body.auto_features['tun_L'], self.side_body.auto_features['tun_R']
        f_img, s_img = self._read_img()
        f_img_cut_L, f_rect_cut_L = self._cut_img(f_img, f_tun_L)
        f_img_cut_R, f_rect_cut_R = self._cut_img(f_img, f_tun_R)
        s_img_cut_L, s_rect_cut_L = self._cut_img(s_img, s_tun_L)
        s_img_cut_R, s_rect_cut_R = self._cut_img(s_img, s_tun_R)
        self.adjust_features['f_tun_L'] = self.adjust_feature_x(f_img_cut_L, f_rect_cut_L)
        self.adjust_features['f_tun_R'] = self.adjust_feature_x(f_img_cut_R, f_rect_cut_R)
        self.adjust_features['s_tun_L'] = self.adjust_feature_x(s_img_cut_L, s_rect_cut_L)
        self.adjust_features['s_tun_R'] = self.adjust_feature_x(s_img_cut_R, s_rect_cut_R)

    def adjust_feature_x(self, img, range_rect):
        # rect_range = dict(range=[left_x, left_y, right_x, right_y], point=(x, y))
        result = 0
        rect = range_rect['range']
        point = range_rect['point']
        x0, y0 = point[0] - rect[0], point[1] - rect[1]
        dst=self._canny(img)
        edgesmat = np.mat(dst)
        h, w = img.shape[:2]
        points = [(j, i) for i in range(h) for j in range(w) if edgesmat[i, j] == 255]
        candidates = [x for x in range(-10, 11) if dst[y0, x0 + x] == 255 and x != 0]
        if candidates:
            candidates = list(filter(lambda x: self._is_edge_point(points, (x0 + x, y0)), candidates))
            return self._nearest(candidates)
        return 0

    def _nearest(self, candidates):
        nearest = 0
        if candidates:
            smallest = abs(candidates[0])
            nearest = candidates[0]
            for x in candidates[1:]:
                if abs(x) < smallest:
                    nearest = x
                    smallest = abs(x)
        return nearest

    def _is_edge_point(self, points, edge_point, thresh_cnt=30):
        outline_transformer = OutlineTransformer(points, edge_point)
        curves = outline_transformer.scan()
        curves = outline_transformer.merge_curves(curves, small_thresh=2)
        for curve in curves:
            if len(curve.curves) >= thresh_cnt:
                return True
        return False

    def _read_img(self):
        f_img_file = self.front_body.img_file
        s_img_file = self.side_body.img_file
        f_img = cv2.imread(f_img_file, 0)
        s_img = cv2.imread(s_img_file, 0)
        return f_img, s_img

    def _cut_img(self, img, pt, up_margin=10, margin=50):
        x, y = pt
        left_x, left_y = x - margin, y - up_margin
        right_x, right_y = x + margin + 1, y + margin + 1
        rect_range = dict(range=[left_x, left_y, right_x, right_y], point=(x, y))
        dst_img = img[left_y:right_y, left_x:right_x]
        return dst_img, rect_range

    def _canny(self, input_img):
        shape = input_img.shape
        gray = input_img
        if len(shape) > 2 and shape[2] > 1:
            gray = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
        img = cv2.GaussianBlur(gray, (3, 3), 0)
        dst = cv2.Canny(img, 30, 200)
        return dst

    def _laplacian(self, input_img):
        shape = input_img.shape
        gray = input_img
        if len(shape) > 2 and shape[2] > 1:
            gray = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
        gray_lap = cv2.Laplacian(gray, cv2.CV_16S, ksize=3)
        dst = cv2.convertScaleAbs(gray_lap)
        return dst

    def _sobel(self, input_img):
        shape = input_img.shape
        gray = input_img
        if len(shape) > 2 and shape[2] > 1:
            gray = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
        imx = np.zeros(gray.shape)
        filters.sobel(gray, 1, imx)
        imy = np.zeros(gray.shape)
        filters.sobel(gray, 0, imy)
        magnitude = np.sqrt(imx ** 2 + imy ** 2)
        magnitude_invert = 255 - magnitude
        return magnitude_invert

    def show_img(self, img, orig_pts, new_pts):
        plt.imshow(img, cmap='gray')
        if orig_pts:
            plt.scatter([x for x, y in orig_pts], [y for x, y in orig_pts], c='b', marker='*')
        if new_pts:
            plt.scatter([x for x, y in new_pts], [y for x, y in new_pts], c='r', marker='+')
        plt.show()

    def show_4_imgs(self, *img_and_pts):
        i = 1
        for img, orig_pts, new_pts in img_and_pts:
            plt.subplot(2, 2, i)
            plt.imshow(img, cmap='gray')
            if orig_pts:
                plt.scatter([x for x, y in orig_pts], [y for x, y in orig_pts], c='b', marker='*')
            if new_pts:
                plt.scatter([x for x, y in new_pts], [y for x, y in new_pts], c='r', marker='+')
            i += 1
            if i > 4:
                break
        plt.show()
