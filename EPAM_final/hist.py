"""
plot histograms: price from microdistrict
                 live square from microdistrict
"""
import matplotlib.pyplot as plt
import pandas as pd


def hist():
    """
    plot histograms

    :return: histogram city.png
    """

    cities = {
        "Mos": "Москва",
        "SPb": "Санкт Петербург",
        "Ekb": "Екатеринбург",
    }

    app_type = {
        "sec": "Secondary",
        "new": "New",
    }

    for city_key, city in cities.items():

        fig = plt.figure(figsize=(80, 60))

        for app, subplot_id in zip(app_type, [(221, 222), (223, 224)]):

            orginal_df = pd.read_excel(
                f"Data_from_web/{city_key}_{app}_app_offers.xlsx"
            )
            df_price = orginal_df[["microdistrict", "price_per_square"]].dropna()
            df_square = orginal_df[["microdistrict", "live_square"]].dropna()
            distr_price = df_price.groupby(["microdistrict"]).mean()
            distr_square = df_square.groupby(["microdistrict"]).mean()

            plt.subplots_adjust(bottom=0.15)

            fig.add_subplot(subplot_id[0])
            plt.bar(distr_price.index, distr_price["price_per_square"])
            plt.title(f"{app_type[app]}", loc="left", fontsize=40)
            plt.xticks(rotation=90)
            plt.yticks(fontsize=40)
            plt.xlabel("Район", fontsize=40)
            plt.ylabel("Цена за квадратный метр, ₽/м²", fontsize=40)

            fig.add_subplot(subplot_id[1])
            plt.bar(distr_square.index, distr_square["live_square"])
            plt.title(f"{app_type[app]}", loc="right", fontsize=40)
            plt.xticks(rotation=90)
            plt.yticks(fontsize=40)
            plt.xlabel("Район", fontsize=40)
            plt.ylabel("Площадь, м²", fontsize=40)
            plt.suptitle(f"{city}", fontsize=60)

        # plt.show()
        plt.savefig(f"Output/{city}.png")
