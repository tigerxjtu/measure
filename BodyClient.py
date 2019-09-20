
from aip import AipBodyAnalysis
from NoBodyException import NoBodyException
from utils import get_file_content,expand_rect
import base64
import numpy as np
import cv2

class BodyClient(object):
    APP_ID = '44eab39f0ed44844b94f487a6e88fdbc'  # 'd90755ad2f2047dbabb12ad0adaa0b03'
    API_KEY = '55e735d6888b46908915f3533a6b7442'  # '22f1025b88f54494bcf5d980697b4b83 '
    SECRET_KEY = '41213cbdaffa483d9ed9a59a24157d4b'  # '4a4b41139c204905be1db659d751355f'

    def __init__(self):
        self.client = AipBodyAnalysis(BodyClient.APP_ID, BodyClient.API_KEY, BodyClient.SECRET_KEY)

    def _body_seg(self,filename):
        image = get_file_content(filename)
        res = self.client.bodySeg(image)
        labelmap = base64.b64decode(res['labelmap'])
        nparr_labelmap = np.fromstring(labelmap, np.uint8)
        labelmapimg = cv2.imdecode(nparr_labelmap, 1)
        im_new_labelmapimg = np.where(labelmapimg == 1, 255, labelmapimg)
        return im_new_labelmapimg

    def _canny_points(self,img,rect=None):
        if rect:
            x,y,w,h = rect
        else:
            x,y=0,0
            h,w = img.shape[:2]
        body = img[y:y + h, x:x + w]
        edges = cv2.Canny(body, 10, 100)
        edgesmat = np.mat(edges)
        points = [(j + x, i + y) for i in range(h) for j in range(w) if edgesmat[i, j] == 255]
        return points

    def body_seg_points(self,filename):
        img_seg=self._body_seg(filename)
        return self._canny_points(img_seg)

    '''
    {'person_num': 2, 'person_info': [{'body_parts': {'left_hip': {'y': 549.78125, 'x': 423.34375, 'score': 0.8641700744628906}, 'top_head': {'y': 295.46875, 'x': 394.0, 'score': 0.8867737650871277}, 'right_mouth_corner': {'y': 344.375, 'x': 384.21875, 'score': 0.8865712285041809}, 'neck': {'y': 363.9375, 'x': 394.0, 'score': 0.8912984728813171}, 'left_shoulder': {'y': 383.5, 'x': 442.90625, 'score': 0.8800243139266968}, 'left_knee': {'y': 657.375, 'x': 433.125, 'score': 0.8804177045822144}, 'left_ankle': {'y': 755.1875, 'x': 423.34375, 'score': 0.8549085855484009}, 'left_mouth_corner': {'y': 344.375, 'x': 403.78125, 'score': 0.8695278763771057}, 'right_elbow': {'y': 442.1875, 'x': 305.96875, 'score': 0.9053295850753784}, 'right_ear': {'y': 324.8125, 'x': 374.4375, 'score': 0.8913755416870117}, 'nose': {'y': 324.8125, 'x': 394.0, 'score': 0.8767616748809814}, 'left_eye': {'y': 315.03125, 'x': 403.78125, 'score': 0.8842508792877197}, 'right_eye': {'y': 315.03125, 'x': 384.21875, 'score': 0.872444748878479}, 'right_hip': {'y': 549.78125, 'x': 374.4375, 'score': 0.8706536293029785}, 'left_wrist': {'y': 491.09375, 'x': 462.46875, 'score': 0.8681846857070923}, 'left_ear': {'y': 324.8125, 'x': 413.5625, 'score': 0.8833358883857727}, 'left_elbow': {'y': 432.40625, 'x': 491.8125, 'score': 0.8757244944572449}, 'right_shoulder': {'y': 383.5, 'x': 345.09375, 'score': 0.8604100942611694}, 'right_ankle': {'y': 755.1875, 'x': 364.65625, 'score': 0.883700966835022}, 'right_knee': {'y': 657.375, 'x': 364.65625, 'score': 0.8726198673248291}, 'right_wrist': {'y': 491.09375, 'x': 335.3125, 'score': 0.8524751663208008}}, 'location': {'height': 522.3967895507812, 'width': 213.4878540039062, 'top': 279.5125427246094, 'score': 0.9985131025314331, 'left': 288.0614013671875}}, {'body_parts': {'left_hip': {'y': 539.0, 'x': 413.25, 'score': 0.2676204741001129}, 'top_head': {'y': 741.5, 'x': 524.625, 'score': 0.0297189150005579}, 'right_mouth_corner': {'y': 478.25, 'x': 463.875, 'score': 0.009633682668209076}, 'neck': {'y': 852.875, 'x': 332.25, 'score': 0.01634016819298267}, 'left_shoulder': {'y': 377.0, 'x': 423.375, 'score': 0.0272684283554554}, 'left_knee': {'y': 650.375, 'x': 423.375, 'score': 0.3098172545433044}, 'left_ankle': {'y': 751.625, 'x': 433.5, 'score': 0.4415453672409058}, 'left_mouth_corner': {'y': 478.25, 'x': 463.875, 'score': 0.01229123119264841}, 'right_elbow': {'y': 427.625, 'x': 494.25, 'score': 0.08809270709753036}, 'right_ear': {'y': 680.75, 'x': 750, 'score': 0.02279716171324253}, 'nose': {'y': 488.375, 'x': 453.75, 'score': 0.02511453814804554}, 'left_eye': {'y': 488.375, 'x': 443.625, 'score': 0.02269705384969711}, 'right_eye': {'y': 751.625, 'x': 750, 'score': 0.02191649936139584}, 'right_hip': {'y': 539.0, 'x': 372.75, 'score': 0.1868444383144379}, 'left_wrist': {'y': 488.375, 'x': 474.0, 'score': 0.3365231156349182}, 'left_ear': {'y': 893.375, 'x': 403.125, 'score': 0.007937739603221416}, 'left_elbow': {'y': 437.75, 'x': 484.125, 'score': 0.1944440901279449}, 'right_shoulder': {'y': 377.0, 'x': 433.5, 'score': 0.02875573188066483}, 'right_ankle': {'y': 751.625, 'x': 423.375, 'score': 0.1604309529066086}, 'right_knee': {'y': 670.625, 'x': 372.75, 'score': 0.1398747861385345}, 'right_wrist': {'y': 488.375, 'x': 474.0, 'score': 0.07319473475217819}}, 'location': {'height': 539.47509765625, 'width': 126.1507263183594, 'top': 458.58251953125, 'score': 0.00636356882750988, 'left': 622.8492431640625}}], 'log_id': 1953527121404955486}
    '''
    def _body_part(self,filename):
        image = get_file_content(filename)
        para = self.client.bodyAnalysis(image)
        person_num=para.get('person_num',0)
        if person_num < 1:
            raise NoBodyException()
        person=para['person_info'][0]
        score = person['location']['score']
        if score < 0.5:
            raise NoBodyException()
        loc = person['location']
        x_left = int(loc['left'])
        y_top = int(loc['top'])
        w = int(loc['width'])
        h = int(loc['height'])
        return person['body_parts'],(x_left,y_top,w,h)

    #top_head, left_ankle, right_ankle
    def body_points(self,filename):
        parts,rect = self._body_part(filename)
        points = {k: (v['x'], v['y']) for k, v in parts.items()}
        return points,rect

    def process_body(self,filename):
        img = cv2.imread(filename)
        height, width = img.shape[:2]
        body_points, rect = self.body_points(filename)

        x_left, y_top, w, h = rect
        new_rect=expand_rect(x_left,y_top,w,h,width,height)

        img_seg = self._body_seg(filename)
        # cv2.imshow("seg",img_seg)
        outline_points = self._canny_points(img_seg, new_rect)
        # print(outline_points)
        return body_points, outline_points, rect


body_client = BodyClient()

if __name__ == '__main__':
    file_path = '201005100004_Front.jpg'#r'C:\dataguru_new\pics\201810\U1000208181024132310246F.jpg'
    file_path = r'C:\dataguru_new\pics\201810\U1000208181024132310246F.jpg'
    body_points, outline_points, rect = body_client.process_body(file_path)
    img = cv2.imread(file_path)
    for point in outline_points:
        cv2.circle(img,point,1,(0,0,255))
    for point in body_points.values():
        cv2.circle(img, (int(point[0]),int(point[1])), 3, (255, 0, 0))
    x_left, y_top, w, h = rect
    cv2.rectangle(img, (x_left, y_top), (x_left + w, y_top + h), (0, 255, 0), 2)
    cv2.imshow("img", img)
    cv2.waitKey()
