
from sklearn.linear_model import LinearRegression
from sklearn.externals import joblib

class LinearModel(object):

    def __init__(self):
        self.model = LinearRegression()

    def fit(self,X_train,Y):
        self.model.fit(X_train,Y)

    def predict(self,X_test):
        return self.model.predict(X_test)

    def predictOne(self,X):
        return self.model.predict(X)[0]

    def save_model(self,model_file):
        joblib.dump(value=self.model,filename=model_file)

    def load_model(self,model_file):
        joblib.dump(filename=model_file)

