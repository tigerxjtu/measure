from model.LinearModel import LinearModel
from ui.Body import FrontBody,SideBody,BackBody
from utils import distance
import os
import numpy as np
from Config import config
from sklearn.preprocessing import PolynomialFeatures



class Xiong3sideModel(LinearModel):

    model_file = 'xiong_3side_linear2.model'
    mean_value = 95
    model = None

    def __init__(self,body_id,height,**args):
        self.body_id = body_id
        self.height = height
        self.model_path = config.model_path
        super().__init__(**args)

    def get_model(self):
        if Xiong3sideModel.model:
            return Xiong3sideModel.model
        Xiong3sideModel.model = self.load_model(os.path.join(self.model_path,Xiong3sideModel.model_file))
        return Xiong3sideModel.model

    def x_data(self):
        front_body = self.get_body(self.body_id,'F')
        features = front_body.calculate_features()
        left, right = features['xiong_L'],features['xiong_R']
        front_distance = distance(left, right)


        side_body = self.get_body(self.body_id,'S')
        features = side_body.calculate_features()
        left, right = features['xiong_L'],features['xiong_R']
        side_distance = distance(left, right)

        back_body = self.get_body(self.body_id, 'B')
        features = back_body.calculate_features()
        left, right = features['xiong_L'], features['xiong_R']
        back_distance = distance(left, right)

        front_height = front_body._max_y - front_body._min_y
        side_height = side_body._max_y - side_body._min_y
        back_height = back_body._max_y - back_body._min_y

        front = front_distance*self.height/front_height
        side = side_distance*self.height/side_height
        back = back_distance*self.height/back_height

        front_min = min(front,back)

        return [front_min,side]

    def predict(self):
        x=self.x_data()
        # print(x)
        # print(powx(*x))
        input = np.array(x)
        input=input.reshape((1,-1))
        # pf = PolynomialFeatures(degree=2)
        # print(input)
        model = self.get_model()

        # print(model.coef_)
        # print(model.intercept_)
        # print(model.coef_,model.intercept_)
        # print(dir(model))
        # print(pf.fit_transform(input))
        # result = model.predict(pf.fit_transform(input))[0]
        result = model.predict(input)[0]
        # print(result)
        return float(result)+Xiong3sideModel.mean_value

# def powx(x1,x2,x3):
#     return [x1**2,x2**2,x3**2,x1*x2,x1*x3,x2*x3]

if __name__ == '__main__':
    neck_model = Xiong3sideModel('U1002295190920221708564',176)
    # print(distance([513, 476],[552, 453]))
    print(neck_model.predict())