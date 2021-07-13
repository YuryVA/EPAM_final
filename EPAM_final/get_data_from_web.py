"""
Get data with apartments offers details from real estate website
"""

import asyncio
from concurrent.futures import ProcessPoolExecutor

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup


def get_htmls(url_list: list):
    """
    return list of htmls from list or urls

    :param url_list: list of urls
    :return: htmls of given urls
    """

    async def fetch_html(client, url: str):
        """
        fetch response from http's
        """

        async with client.get(url) as resp:
            return await resp.text()

    async def get_task(urls: list):
        """
        get html pages
        """

        async with aiohttp.ClientSession() as client:
            task = [asyncio.create_task(fetch_html(client, url)) for url in urls]
            await asyncio.gather(*task)

        return task

    loop = asyncio.get_event_loop()
    htmls = loop.run_until_complete(get_task(url_list))

    return htmls


def get_links(html: str) -> list:
    """
    parse given html and
    create list - [
                    app1 offer link,
                    app2 offer link,
                    app3 offer link,
                    ...
                    ]
                    from 1 website page

    :param html: 1 page from website with offers
    :return: list of links from 1 page
    """

    links = []
    soup = BeautifulSoup(html, features="html.parser")
    for href in soup.find_all("div", class_="offer__headline"):
        link = f'https://www.realtymag.ru{href.a.get("href")}'
        links.append(link)

    return links


def get_offers(html: str) -> dict:
    """
    parse given html and
    create dict - {
                  "live_square": live_square
                  "microdistrict": microdistrict,
                  "price_per_square": price_per_square,
                  "location_lat": location_lat,
                  "location_long": location_long,
                  "refresh_time": refresh_time,
                  }

    :param html: offers page html
    :return: offers data dict
    """

    soup = BeautifulSoup(html, features="html.parser")

    try:
        live_square_section = soup.find(
            "div", class_="offer-detail__section-item section_type_full-square"
        )
        live_square = live_square_section.find(
            "div", class_="offer-detail__section-item-body"
        ).get_text()
        live_square = float(live_square.split()[0])
    except AttributeError:
        live_square = None

    try:
        microdistrict = soup.find("div", class_="offer-detail__sublocality").get_text()
    except AttributeError:
        microdistrict = None

    try:
        price_per_square = soup.find(
            "div", class_="offer-detail__price-per-square-rur"
        ).get_text()
        price_per_square = price_per_square.rstrip("₽/м²")
        price_per_square = float("".join(price_per_square.split()))
    except AttributeError:
        price_per_square = None

    try:
        location_section = soup.find("div", class_="offer-detail__map")
        text = location_section.find_next("script").string
        location_lat = float(text.split(",")[1])
        location_long = float(text.split(",")[2].split(")")[0])
    except AttributeError:
        location_lat = None
        location_long = None

    try:
        refresh_time = soup.find("div", class_="offer-detail__refresh").get_text()
    except AttributeError:
        refresh_time = None

    offer_data = {
        "live_square": live_square,
        "microdistrict": microdistrict,
        "price_per_square": price_per_square,
        "location_lat": location_lat,
        "location_long": location_long,
        "refresh_time": refresh_time,
    }

    return offer_data


def get_list_offers_link(url, step) -> list:
    """
    create pool of "step" website pages to get offers urls in parallel

    :param url: website url
    :param step: step of pool
    :return: list of offers urls from pool of "steps" pages
    """

    url_list = [f"{url}&page={i}" for i in range(step, step + 20)]
    offers_links_list = []

    ayo_html_pages = get_htmls(url_list)
    html_pages = [html.result() for html in ayo_html_pages]

    if __name__ == "__main__":
        with ProcessPoolExecutor() as pool:
            result = pool.map(get_links, html_pages)
            for res in result:
                offers_links_list.extend(res)

    return offers_links_list


def get_offers_data(offers_links_list):
    """
    from pool of "step" offers links get offers data in parallel

    :param offers_links_list: offers urls list
    :return: pandas.DataFrame with offers data
    """

    offers_df = pd.DataFrame(
        columns=[
            "offer_id",
            "price_per_square",
            "live_square",
            "microdistrict",
            "location_lat",
            "location_long",
            "refresh_time",
        ]
    )

    ayo_html_offers = get_htmls(offers_links_list)
    html_offers = [html.result() for html in ayo_html_offers]

    if __name__ == "__main__":
        with ProcessPoolExecutor() as pool:
            for link, data_dict in zip(
                offers_links_list, pool.map(get_offers, html_offers)
            ):
                offer_id = link.split("/")[-1]
                data_dict["offer_id"] = offer_id
                offers_df = offers_df.append(data_dict, ignore_index=True)

    return offers_df


def create_links_file(cities, app_type):
    """
    write list of offers urls to file "city_key_app_key_links.txt"

    :param cities: dict {
                         city_key_1: city 1,
                         city_key_2: city 2,
                         ...
                         }
    :param app_type: dict {
                           app_key_1: apartment type 1,
                           app_key_2: apartment type 2,
                           ...
                           }
    """

    for city_key, city in cities.items():
        for app_key, app in app_type.items():
            url = f"https://www.realtymag.ru/{city}/{app}/prodazha/?type=1&currency=RUR&price_type=all"
            offers_link_list = []

            if app_key == "new" and city_key == "Ekb":
                for step in range(1, 140, 20):
                    offers_link_list.extend(get_list_offers_link(url, step))
                    # print(step)
            else:
                for step in range(1, 240, 20):
                    offers_link_list.extend(get_list_offers_link(url, step))
                    # print(step)

            with open(f"Data_from_web/{city_key}_{app_key}_links.txt", "w") as f_out:
                f_out.write("\n".join(offers_link_list))


def main():
    """
    create excel files with offers data "city_key_app_key_app_offers.xlsx"
    """

    cities = {
        "Mos": "moskva",
        "SPb": "sankt-peterburg",
        "Ekb": "sverdlovskaya-oblast/ekaterinburg",
    }

    app_type = {
        "sec": "kvartira",
        "new": "novostroyka",
    }

    # Create file with offers urls 'city_key_app_key_links.txt'
    create_links_file(cities, app_type)

    for city in cities:
        for app in app_type:

            offers_df = pd.DataFrame(
                columns=[
                    "offer_id",
                    "price_per_square",
                    "live_square",
                    "microdistrict",
                    "location_lat",
                    "location_long",
                    "refresh_time",
                ]
            )

            # Read urls from file
            with open(f"Data_from_web/{city}_{app}_links.txt") as file:

                offers_links_list = file.read().splitlines()

                for step in range(0, 5000, 50):
                    sub_list = offers_links_list[step : step + 50]
                    # print(sub_list)
                    offers_df = offers_df.append(
                        get_offers_data(sub_list), ignore_index=True
                    )
                    # print(step)

            offers_df.to_excel(f"Data_from_web/{city}_{app}_app_offers.xlsx")


if __name__ == "__main__":
    main()
