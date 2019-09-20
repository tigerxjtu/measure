from model.LinearModel import LinearModel
from utils import distance
import os
import numpy as np
from Config import config



class ShoulderModel(LinearModel):

    model_file = 'shoulder.model'
    mean_value = 42
    model = None

    def __init__(self,body_id,height,**args):
        self.body_id = body_id
        self.height = height
        self.model_path = config.model_path
        super().__init__(**args)

    def get_model(self):
        if ShoulderModel.model:
            return ShoulderModel.model
        ShoulderModel.model = self.load_model(os.path.join(self.model_path,ShoulderModel.model_file))
        return ShoulderModel.model

    def x_data(self):
        front_body = self.get_body(self.body_id, 'F')
        front_body.load_feature()
        if front_body.bottom_y:
            front_height = front_body.bottom_y - front_body.top_head_point[1]
        else:
            front_height = front_body._max_y - front_body._min_y
        left, right = front_body.process_shoulder_feature()
        front_distance = distance(left, right)
        front = front_distance*self.height/front_height

        back_body = self.get_body(self.body_id, 'B')
        back_body.load_feature()
        if back_body.bottom_y:
            back_height = back_body.bottom_y - back_body.top_head_point[1]
        else:
            back_height = back_body._max_y - back_body._min_y
        left, right = back_body.process_shoulder_feature()
        back_distance = distance(left, right)
        back = back_distance * self.height / back_height

        return [front,back]

    def predict(self):
        x=self.x_data()
        # print(x)
        input = np.array(x)
        input=input.reshape((1,-1))
        # print(input)
        model = self.get_model()
        # print(model.coef_,model.intercept_)
        # print(dir(model))
        result = model.predict(input)[0]
        # print(result)
        return float(result)+ShoulderModel.mean_value

if __name__ == '__main__':
    model = ShoulderModel('U1002218190901092552964',176)
    # print(distance([513, 476],[552, 453]))
    print(model.predict())