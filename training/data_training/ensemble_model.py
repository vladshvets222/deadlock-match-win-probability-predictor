import numpy as np

class EnsembleModel:

    def __init__(self, xgb_model, cat_model):
        self.xgb_model = xgb_model
        self.cat_model = cat_model

    def predict_proba(self, X):

        pred1 = self.xgb_model.predict_proba(X)
        pred2 = self.cat_model.predict_proba(X)

        return (pred1+pred2) / 2
    
    def predict(self, X):

        probs = self.predict_proba(X)[:, 1]

        return (probs > 0.5).astype(int)
    