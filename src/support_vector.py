from sklearn import svm


class CalcSupportVector:
    """
    Support Vector Class
    """
    def __init__(self):
        self.model = svm.LinearSVC()

    def training(self, data, target):
        self.model.fit(data, target)

    def prediction(self, data):
        result = self.model.predict(data)
        return result
