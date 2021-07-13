"""
plot prices heatmap
"""

import math

import folium
import geopandas as gpd


def bins_thresholds(prices) -> list:
    """
    generate colors bin edges

    :param prices: prices pandas.Series
    :return: bins list
    """
    max_price = math.ceil(prices.max())
    min_price = math.floor(prices.min())
    prices_10 = round(prices.quantile(q=0.05))
    prices_90 = round(prices.quantile(q=0.95))
    delta_12 = round((prices_10 - min_price) / 2)
    delta_89 = round((max_price - prices_90) / 2)
    delta_37 = round((prices_90 - prices_10) / 5)
    bins = [
        min_price,
        min_price + delta_12,
        prices_10,
        prices_10 + delta_37,
        prices_10 + 2 * delta_37,
        prices_10 + 3 * delta_37,
        prices_10 + 4 * delta_37,
        prices_90,
        prices_90 + delta_89,
        max_price,
    ]
    return bins


def plot():
    """
    plot prices heatmap

    :return: html file with choropleth map with prices
    """

    cities = {
        "Mos": [55.755819, 37.617644],
        "SPb": [59.939099, 30.315877],
        "Ekb": [56.838011, 60.597474],
    }

    app_type = {
        "sec": "Secondary",
        # "new": "New",
    }

    for city, loc in cities.items():

        for app_key, app in app_type.items():

            heatmap = folium.Map(
                location=loc,
                width="70%",
                height="70%",
                left="15%",
                top="15%",
                zoom_start=10,
                control_scale=True,
                tiles="cartodbpositron",
            )

            data_type = {
                "real": f"Data_preproc/{city}_{app_key}_grid_gpd.gpkg",
                "predict": f"Data_predict/{city}_{app_key}_predict.gpkg",
            }

            for data_key, value in data_type.items():

                prices = gpd.read_file(value)
                prices["price_per_"] = prices["price_per_"] / 1000
                prices = prices.rename(columns={"price_per_": "price_per_square"})

                bins = bins_thresholds(prices["price_per_square"])
                layer_show = data_key == "real"

                folium.Choropleth(
                    geo_data=prices,
                    name=f"{app}_{data_key}",
                    data=prices,
                    columns=["geoid", "price_per_square"],
                    key_on="feature.id",
                    fill_color="YlOrRd",
                    bins=bins,
                    fill_opacity=0.5,
                    line_weight=0,
                    line_opacity=0,
                    smooth_factor=0.5,
                    legend_name=f"{data_key}: thousands ₽/m²",
                    show=layer_show,
                ).add_to(heatmap)

            folium.LayerControl(collapsed=False).add_to(heatmap)
            heatmap.save(f"Output/{city}_{app_key}.html")


if __name__ == "__main__":
    plot()
