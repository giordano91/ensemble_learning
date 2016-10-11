from sklearn.naive_bayes import GaussianNB


class CalcNaiveBayes:
    """
    Naive Bayes class
    """
    def __init__(self):
        self.model = GaussianNB()

    def training(self, data, target):
        self.model.fit(data, target)

    def prediction(self, data):
        result = self.model.predict(data)
        return result
