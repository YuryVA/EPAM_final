"""
Make predictions for city grid polygons without price
"""

import geopandas as gpd
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsRegressor


def point_to_coord(gdf):
    """
    modified column GeoSeries 'centroids' to numpy.array 'coordinates'

    :param gdf: input GeoPandasDataFrame
    :return: GeoPandasDataFrame
    """

    new_gdf = gpd.GeoDataFrame(columns=["centroid"])
    new_gdf["centroid"] = gdf
    coordinates = []

    for row in new_gdf["centroid"]:
        coordinates.append(np.array(row.coords[0]))
    new_gdf["coordinates"] = coordinates

    return new_gdf


def predictions():
    """
    - make predictions
    - save them to GeoPandasDataFrame

    :return: GeoPandasDataFrame with predictions
    """

    cities = {
        "Mos": "Mos",
        "SPb": "SPb",
        "Ekb": "Ekb",
    }

    app_type = {
        "sec": "kvartira",
        "new": "novostroyka",
    }

    for city in cities:
        for app in app_type:
            # подготавливаем датафрейм с данными для обучения модели
            city_grid_prices = gpd.read_file(f"Data_preproc/{city}_{app}_grid_gpd.gpkg")
            city_grid_prices = city_grid_prices.rename(
                columns={"price_per_": "price_per_square"}
            )
            # добавляем столбец 'centroid' и 'coordinates'
            city_grid_prices["centroid"] = city_grid_prices["geometry"].centroid
            city_grid_prices = city_grid_prices.merge(
                point_to_coord(city_grid_prices["centroid"]), on="centroid"
            )
            city_grid_train = city_grid_prices[
                city_grid_prices["price_per_square"] > 50000
            ]
            # подготавливаем датафрейм с полигонами для предсказаний цены
            city_grid = gpd.read_file(f"Data_preproc/grid_{city}_bound.gpkg").drop(
                "FID", axis=1
            )
            # city_grid['price_per_square'] = np.zeros(city_grid.shape[0])
            # добавляем столбец 'centroid' и 'coordinates'
            city_grid["centroid"] = city_grid["geometry"].centroid
            city_grid_predict = city_grid.merge(
                point_to_coord(city_grid["centroid"]), on="centroid"
            )
            # обучаем модель
            X_train, y_train = (
                city_grid_train["coordinates"].values.tolist(),
                city_grid_train["price_per_square"].values.tolist(),
            )
            mod = KNeighborsRegressor()
            mod_parameters = {
                "n_neighbors": range(2, 40, 2),
                "weights": ["distance", "uniform"],
            }
            GSCV = GridSearchCV(mod, param_grid=mod_parameters, n_jobs=-1)
            GSCV.fit(X_train, y_train)
            city_grid_predict["price_per_square"] = GSCV.predict(
                city_grid_predict["coordinates"].values.tolist()
            )

            # print(GSCV.best_params_)
            # print(GSCV.best_score_)
            # print(city_grid_prices["price_per_square"].describe())
            # print(city_grid_predict["price_per_square"].describe())
            # сохраняем предсказани я в файл
            city_grid_predict["geoid"] = city_grid_predict.index.astype(str)
            city_grid_to_viz = city_grid_predict[
                ["geoid", "price_per_square", "geometry"]
            ]
            city_grid_to_viz.to_file(f"Data_predict/{city}_{app}_predict.gpkg")
