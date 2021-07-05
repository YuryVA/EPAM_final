"""
plot prices heatmap
"""

import folium
import geopandas as gpd


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
                prices = prices.rename(columns={"price_per_": "price_per_square"})

                if data_key == "real":
                    layer_show = True
                else:
                    layer_show = False

                folium.Choropleth(
                    geo_data=prices,
                    name=f"{app}_{data_key}",
                    data=prices,
                    columns=["geoid", "price_per_square"],
                    key_on="feature.id",
                    fill_color="YlOrRd",
                    bins=9,
                    fill_opacity=0.5,
                    line_weight=0,
                    line_opacity=0,
                    smooth_factor=0.5,
                    # threshold_scale=[20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000],
                    legend_name=f"Price per square {data_key}",
                    show=layer_show,
                ).add_to(heatmap)

            folium.LayerControl().add_to(heatmap)

            heatmap.save(f"Output/{city}_{app_key}.html")
