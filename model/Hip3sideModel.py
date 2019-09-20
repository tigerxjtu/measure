from model.LinearModel import LinearModel
from ui.Body import FrontBody,SideBody,BackBody
from utils import distance
import os
import numpy as np
from Config import config
from sklearn.preprocessing import PolynomialFeatures



class Hip3sideModel(LinearModel):

    model_file = 'hip_3side.model'
    mean_value = 97
    model = None

    def __init__(self,body_id,height,**args):
        self.body_id = body_id
        self.height = height
        self.model_path = config.model_path
        super().__init__(**args)

    def get_model(self):
        if Hip3sideModel.model:
            return Hip3sideModel.model
        Hip3sideModel.model = self.load_model(os.path.join(self.model_path,Hip3sideModel.model_file))
        return Hip3sideModel.model

    def x_data(self):
        front_body = self.get_body(self.body_id,'F')
        front_body.load_feature()
        if front_body.bottom_y:
            front_height = front_body.bottom_y - front_body.top_head_point[1]
        else:
            front_height = front_body._max_y - front_body._min_y
        left, right = front_body.process_hip_feature()
        front_distance = distance(left, right)


        side_body = self.get_body(self.body_id,'S')
        side_body.load_feature()
        left, right = side_body.process_hip_feature()
        side_distance = distance(left, right)
        if side_body.bottom_y:
            side_height = side_body.bottom_y - side_body.top_head_point[1]
        else:
            side_height = side_body._max_y - side_body._min_y

        back_body = self.get_body(self.body_id, 'B')
        back_body.load_feature()
        if back_body.bottom_y:
            back_height = back_body.bottom_y - back_body.top_head_point[1]
        else:
            back_height = back_body._max_y - back_body._min_y
        left, right = back_body.process_hip_feature()
        back_distance = distance(left, right)

        front = front_distance*self.height/front_height
        side = side_distance*self.height/side_height
        back = back_distance*self.height/back_height

        return [front,side,back]

    def predict(self):
        x=self.x_data()
        input = np.array(x)
        # print(input)
        input=input.reshape((1,-1))
        pf = PolynomialFeatures(degree=2)
        # print(input)
        model = self.get_model()
        # print(model.coef_,model.intercept_)
        # print(dir(model))
        result = model.predict(pf.fit_transform(input))[0]
        # print(result)
        return float(result)+Hip3sideModel.mean_value

if __name__ == '__main__':
    hip_model = Hip3sideModel('U1002217190901092403591',176)
    # print(distance([513, 476],[552, 453]))
    print(hip_model.predict())