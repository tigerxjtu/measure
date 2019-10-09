from model.LinearModel import LinearModel
from utils import distance
import os
import numpy as np
from Config import config



class MainBodyModel(LinearModel):

    model_file = 'main_body_xiong.model'
    mean_value = 0
    model = None

    def __init__(self,body_id,height,**args):
        self.body_id = body_id
        self.height = height
        self.model_path = config.model_path
        super().__init__(**args)

    def get_model(self):
        if MainBodyModel.model:
            return MainBodyModel.model
        MainBodyModel.model = self.load_model(os.path.join(self.model_path,MainBodyModel.model_file))
        return MainBodyModel.model

    def x_data(self):
        front_body = self.get_body(self.body_id, 'F')
        front_body.calculate_features()
        front_distance = np.percentile(front_body.get_main_distances(),[0,25,50,75,100])
        front_height = front_body._max_y - front_body._min_y
        front = front_distance*self.height/front_height

        side_body = self.get_body(self.body_id, 'S')
        side_body.calculate_features()
        side_height = side_body._max_y - side_body._min_y
        side_distance = np.percentile(side_body.get_main_distances(),[0,25,50,75,100])
        side = side_distance * self.height / side_height

        return front.tolist()+side.tolist()

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
        return result

if __name__ == '__main__':
    model = MainBodyModel('U1002218190901092552964',176)
    # print(distance([513, 476],[552, 453]))
    print(model.predict())