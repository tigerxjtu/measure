import cv2
import numpy as np

img = cv2.imread("f_yao_L.jpg",0)

img = cv2.GaussianBlur(img,(3,3),0)
canny = cv2.Canny(img, 30, 200)
print(canny.shape,canny)

# cv2.imshow('Canny',canny)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
import matplotlib.pyplot as plt
plt.imshow(canny,cmap='gray')
plt.show()