# x1,y1=318,263
# x2,y2=408,263
# x,y=464,263
#
# a1=(y-y1)/(x-x1)
# a2=(y-y2)/(x-x2)
# a3=(y2-y1)/(x2-x1)
#
# print(a1,a2,a3)
#
# print(1080/1440)
# print(600/1080)

# a=[(10,2),(11,3),(5,1),(6,1),(4,1)]
# p=min(a,key=lambda x:x[1])
# print(p)

# i=0
# while i<10:
#     print(i)
#     # if i>7:
#     #     break
#     i+=1
# else:
#     print('no break',i)


a=[1,2,3,4]
for i,ele in enumerate(a[1:]):
    print(i,ele)

items = ['a','b','c','d']

import numpy as np
a = np.array([1,2,3])
b = np.array([4,5,6])
print(zip(a,b))
for i,j in zip(a,b):
    print(i,j)