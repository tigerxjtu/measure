from model.LinearModel import LinearModel
from ui.Body import FrontBody,SideBody
from utils import distance
import os
import numpy as np
from Config import config



class NeckModel(LinearModel):

    model_file = 'neck.model'
    mean_value = 40
    model = None

    def __init__(self,body_id,height,**args):
        self.body_id = body_id
        self.height = height
        self.model_path = config.model_path
        super().__init__(**args)

    def get_model(self):
        if NeckModel.model:
            return NeckModel.model
        NeckModel.model = self.load_model(os.path.join(self.model_path,NeckModel.model_file))
        return NeckModel.model

    def x_data(self):
        body = FrontBody(self.body_id)
        body.load_feature()
        left, right = body.features['neck_left_L'], body.features['neck_left_R']
        front_distance = distance(left, right)
        front_height = body.bottom_y - body.top_head_point[1]

        side_body = SideBody(self.body_id)
        side_body.load_feature()
        left, right = side_body.features['neck_left_L'], side_body.features['neck_left_R']
        # print(left,right)
        side_distance = distance(left, right)
        side_height = side_body.bottom_y - side_body.top_head_point[1]
        # print(front_distance,front_height,side_distance,side_height)

        front = front_distance*self.height/front_height
        side = side_distance*self.height/side_height

        return [front,side,front**2,side**2,front*side]

    def predict(self):
        x=self.x_data()
        input = np.array(x)
        input=input.reshape((1,-1))
        # print(input)
        model = self.get_model()
        # print(model.coef_,model.intercept_)
        # print(dir(model))
        result = model.predict(input)[0]
        # print(result)
        return float(result)+NeckModel.mean_value

if __name__ == '__main__':
    neck_model = NeckModel('U1002295190920221708564',176)
    # print(distance([513, 476],[552, 453]))
    print(neck_model.predict())