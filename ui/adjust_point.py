import cv2
import json

files=['f_yao_L','f_yao_R','s_yao_L','s_yao_R']
file=files[3]

json_file=file+'.json'
with open(json_file) as fp:
    json=json.load(fp)
    cut_range=json['range']
    point=json['point']
    x0,y0= point[0] - cut_range[0], point[1] - cut_range[1]

img_file=file+'.jpg'
img=cv2.imread(img_file,0)
print(img.shape)
# gray_lap = cv2.Laplacian(img, cv2.CV_16S, ksize=3)
# dst = cv2.convertScaleAbs(gray_lap)

img = cv2.GaussianBlur(img,(3,3),0)
dst = cv2.Canny(img, 30, 200)

print(dst,(x0,y0))
print(dst[y0,x0-5:x0+5])
candidates=[x for x in range(-10, 11) if dst[y0,x0+x] == 255 and x!=0]
print(candidates)
# print([x for x in range(-10,11)])
# cv2.circle(dst,(x0,y0),2,255,1)
# cv2.imshow('img',dst)
# cv2.waitKey(0)
import matplotlib.pyplot as plt
plt.imshow(dst,cmap='gray')
plt.scatter([x0],[y0],c='r',marker='+')
# plt.scatter(new_pts,c='blue',marker='+')
plt.show()
