"""
Prepare data get from web to make predictions and draw on map
"""

import json

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Polygon


def offers_data_prep(file_name):
    """
    create new column "coordinates"  = (longitude, latitude)
    apartments with the same coordinates replaced one with mean price
    drop unnecessary columns

    :param file_name: name of file with offers data
    :return: pandas.DataFrame with modified data
    """

    orginal_df = pd.read_excel(f"{file_name}")[
        ["price_per_square", "location_long", "location_lat"]
    ].dropna()
    orginal_df["coordinates"] = pd.Series(
        orginal_df["location_long"].astype(str)
        + ", "
        + orginal_df["location_lat"].astype(str)
    )

    df_new = pd.DataFrame(
        columns=["price_per_square", "coordinates", "location_long", "location_lat"]
    )

    for pair in orginal_df["coordinates"].unique():
        price = orginal_df[orginal_df["coordinates"] == pair]["price_per_square"].mean()
        loc_lat = orginal_df[orginal_df["coordinates"] == pair]["location_lat"].iloc[0]
        loc_long = orginal_df[orginal_df["coordinates"] == pair]["location_long"].iloc[
            0
        ]
        df_new = df_new.append(
            pd.Series([price, pair, loc_long, loc_lat], index=df_new.columns),
            ignore_index=True,
        )

    return df_new


def gdf_drop_unique(gdf):
    """
    - create GeoPandasDataFrame where similar polygons with the same coordinates
    replaced one with mean price
    - create column "geoid"

    :param gdf: GeoPandasDataFrame with several prices to one polygon
    :return: GeoPandasDataFrame with mean price to one polygon
    """

    gdf_new = gpd.GeoDataFrame(columns=["price_per_square", "geometry"])

    for coord in gdf["geometry"].unique():
        price = gdf[gdf["geometry"] == coord]["price_per_square"].mean()
        geometry = gdf[gdf["geometry"] == coord]["geometry"].iloc[0]
        gdf_new = gdf_new.append(
            {"price_per_square": price, "geometry": geometry}, ignore_index=True
        )

    gdf_new["geoid"] = gdf_new.index.astype(str)

    return gdf_new


def get_min_max_cord(json_file_name, city):
    """
    get max latitude, max longitude, min latitude, min longitude from json file with city borders

    :param json_file_name: json file with city borders
    :param city: city name
    :return: max latitude, max longitude, min latitude, min longitude of city borders
    """

    max_lat = 0
    max_long = 0
    min_lat = 90
    min_long = 180

    with open(json_file_name) as file:
        cord = json.loads(file.read())
        for poly in cord["coordinates"]:
            if city != "Ekb":
                poly = poly[0]
            for pair in poly:
                lat = pair[0]
                long = pair[1]
                if lat > max_lat:
                    max_lat = lat
                if long > max_long:
                    max_long = long
                if lat < min_lat:
                    min_lat = lat
                if long < min_long:
                    min_long = long

        return max_lat, max_long, min_lat, min_long


def get_grid(max_lat, max_long, min_lat, min_long, step_lat=0.004, step_long=0.0025):
    """
    Create polygon grid dataframe from min, max coordinates

    :param max_lat: max latitude of city borders
    :param max_long: max longitude of city borders
    :param min_lat: min latitude of city borders
    :param min_long: min longitude of city borders
    :param step_lat: grid step on latitude
    :param step_long: grid step on latitude
    :return: GeoPandasDataFrame polygon grid
    """

    grid_gdf = gpd.GeoDataFrame()

    delta_lat = max_lat - min_lat
    delta_long = max_long - min_long
    n_lat = delta_lat / step_lat
    n_long = delta_long / step_long

    lat_array = np.linspace(min_lat, max_lat, num=int(n_lat))
    long_array = np.linspace(min_long, max_long, num=int(n_long))
    len_lat = len(lat_array)
    len_long = len(long_array)

    for i, long in enumerate(long_array):
        for j, lat in enumerate(lat_array):
            print(i, j)
            if i < (len_long - 1) and j < (len_lat - 1):
                long_points = [long, long, long_array[i + 1], long_array[i + 1], long]
                lat_points = [lat, lat_array[j + 1], lat_array[j + 1], lat, lat]
                geometry = Polygon(zip(lat_points, long_points))
                square = gpd.GeoDataFrame(index=[0], geometry=[geometry])
                grid_gdf = grid_gdf.append(square)

    return grid_gdf


def main():
    """
    prepare data from 'city_app_app_offers.xlsx'
    create polygonal grid of the city with mean prices for polygons

    :return:
    grid from nim, max coordinates in 'grid_city.shp' file
    grid in city bounds without water objects in 'grid_city_bound.gpkg' file
    grid with mean prices in 'city_app_grid_gpd.gpkg' file
    """

    cities = ["Mos", "SPb", "Ekb"]
    app_type = ["sec", "new"]

    for city in cities:
        # границы города JSON
        geo_city = f"Data_preproc/{city}_geo.json"
        city_border = gpd.read_file(geo_city)
        # мин и макс координаты границ города
        max_lat, max_long, min_lat, min_long = get_min_max_cord(geo_city, city)
        # строим сетку по мин макс координатам
        grid_df = get_grid(max_lat, max_long, min_lat, min_long)
        # сохраняем сетку в файл
        grid_df.to_file(f"Data_preproc/grid_{city}.shp")
        # читаем сетку из файла
        grid_df = gpd.read_file(f"Data_preproc/grid_{city}.shp").drop("FID", axis=1)
        grid_df = grid_df.set_crs(epsg=4326)

        if city == "SPb":
            # границы береговой линии финского залива
            geo_fin_gulf = "Data_preproc/Fin_gulf_geo.json"
            fin_gulf_border = gpd.read_file(geo_fin_gulf)
            # строим полигональную сетку в границах города без Финского залива
            # сохраняем в файл
            grid_city_bound = grid_df[grid_df.within(city_border.at[0, "geometry"])]
            grid_city_bound_fin_out = grid_city_bound[
                grid_city_bound.disjoint(fin_gulf_border.at[0, "geometry"])
            ]
            grid_city_bound_fin_out.to_file(f"Data_preproc/grid_{city}_bound.gpkg")
            # print(f"сохранили сетку в границах {city} в файл")
        elif city == "Ekb":
            # строим полигональную сетку в границах города без водоемов
            # сохраняем в файл
            grid_city_bound = grid_df[grid_df.within(city_border.at[0, "geometry"])]

            for i in range(1, 6):
                vod = f"Data_preproc/{city}_vod{i}.json"
                vod_border = gpd.read_file(vod)
                grid_city_bound = grid_city_bound[
                    grid_city_bound.disjoint(vod_border.at[0, "geometry"])
                ]

            grid_city_bound.to_file(f"Data_preproc/grid_{city}_bound.gpkg")
            # print(f"сохранили сетку в границах {city} в файл")
        else:
            # строим полигональную сетку в границах города
            # сохраняем в файл
            grid_city_bound = grid_df[
                grid_df.within(city_border.at[0, "geometry"])
            ]  # сетка в границах города
            grid_city_bound.to_file(
                f"Data_preproc/grid_{city}_bound.gpkg"
            )  # сохраняем сетку в границах города в файл
            # print(f"сохранили сетку в границах {city} в файл")

        for app in app_type:
            # дынные из объявлений с усредненной ценой по одинковым точкам
            city_df_unique = offers_data_prep(
                f"Data_from_web/{city}_{app}_app_offers.xlsx"
            )
            #  читаем сетку в границах города из файла
            grid_city_bound = gpd.read_file(f"Data_preproc/grid_{city}_bound.gpkg")
            # данные из объявлений переводим в геофрэйм
            city_gdf_unique = gpd.GeoDataFrame(
                city_df_unique,
                geometry=gpd.points_from_xy(
                    city_df_unique.location_long, city_df_unique.location_lat
                ),
            )
            city_gdf_unique["geoid"] = city_gdf_unique.index.astype(str)
            city_gdf = city_gdf_unique[["price_per_square", "geometry"]]
            city_gdf = city_gdf.set_crs(epsg=4326)
            # привязываем к полигонаальной сетке цены из объявлений
            city_grid_temp = gpd.sjoin(
                grid_city_bound, city_gdf, how="inner", op="contains"
            )
            city_grid_temp["geoid"] = city_grid_temp.index.astype(str)
            city_grid_temp = city_grid_temp[["geoid", "price_per_square", "geometry"]]
            # усредняем цену по каждому полигону
            # сохраняем в файл
            city_grid_prices = gdf_drop_unique(city_grid_temp)
            city_grid_prices = city_grid_prices.set_crs(epsg=4326)
            city_grid_prices.to_file(f"Data_preproc/{city}_{app}_grid_gpd.gpkg")
            # print(f"сохранили сетка с усредненной ценой {city} {app} в файл")


if __name__ == "__main__":
    main()
