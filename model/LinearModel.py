
from sklearn.linear_model import LinearRegression
from sklearn.externals import joblib
from ui.Body import FrontBody,SideBody,BackBody

class LinearModel(object):

    def __init__(self,**args):
        self.model = LinearRegression()
        self.args = args
        # print(self.args)

    def fit(self,X_train,Y):
        self.model.fit(X_train,Y)

    def predict(self,X_test):
        return self.model.predict(X_test)

    def predictOne(self,X):
        return self.model.predict(X)[0]

    def save_model(self,model_file):
        joblib.dump(value=self.model,filename=model_file)

    def load_model(self,model_file):
        return joblib.load(filename=model_file)

    def get_body(self,id, tag):
        if tag == 'F':
            if self.args:
                folder = self.args['folder']
                person_id = self.args['person_id']
                body = FrontBody(id,folder,person_id)
            else:
                body = FrontBody(id)
        elif tag == 'B':
            if self.args:
                folder = self.args['folder']
                person_id = self.args['person_id']
                body = BackBody(id,folder,person_id)
            else:
                body = BackBody(id)
        else:
            if self.args:
                folder = self.args['folder']
                person_id = self.args['person_id']
                body = SideBody(id,folder,person_id)
            else:
                body = SideBody(id)
        body.load_outline()
        body.load_pre_feature()
        return body

