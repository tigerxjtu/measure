

class PtTransformer(object):

    def __init__(self,cent_x,bottom_y):
        self.center_x = cent_x
        self.bottom_y = bottom_y

    def transform(self,x,y,ratio=1):
        new_x = x - self.center_x
        new_y = self.bottom_y - y
        return new_x*ratio, new_y*ratio

    def revserse_transform(self, new_x, new_y, ratio=1):
        x = new_x*ratio+self.center_x
        y = self.bottom_y - new_y*ratio
        return x,y

    def transorm_y(self,y,ratio=1):
        new_y = self.bottom_y - y
        return new_y*ratio

    def reverse_transform_y(self, new_y, ratio=1):
        y=self.bottom_y - new_y*ratio
        return y

    def transform_str(self, x, y, ratio=1):
        new_x, new_y = self.transform(x,y,ratio)
        return '{},{}'.format(new_x,new_y)

if __name__ == '__main__':
    pf=PtTransformer(10,10)
    print(pf.transform_str(0,0))
    print(pf.transform_str(20, 20))

    print(pf.revserse_transform(-10,10))