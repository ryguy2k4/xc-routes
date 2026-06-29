from sklearn.base import BaseEstimator, TransformerMixin
import h3

class TrackCellTransformer(TransformerMixin, BaseEstimator):
    def __init__(self, cell_res):
        self.cell_res = cell_res

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.iloc[:, 0].apply(
                lambda track: " ".join(
                    h3.latlng_to_cell(lat, lon, res=self.cell_res)
                    for line in track.geoms
                    for lat, lon in line.coords
                )
            )