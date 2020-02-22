import numpy as np
from .base import BaseModel


class Dummy(BaseModel):
    def __init__(self, pre_processor):
        super().__init__(pre_processor)
        assert pre_processor.label_type == 'align'

    def fit(self, X, y):
        pass

    def evaluate(self, X, y):
        return 0

    def predict(self, X):
        return np.ones(len(X))

    def save(self, fp):
        with open(fp, 'w'):
            pass

    def load(self, fp):
        pass
