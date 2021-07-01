"""
test html parsers
"""

from get_data_from_web import get_links, get_offers


def test_get_links():
    """
    test function return list of offers links
    """

    links_list = [
        "https://www.realtymag.ru/kvartira/prodazha/2517553691",
        "https://www.realtymag.ru/kvartira/prodazha/2671418108",
        "https://www.realtymag.ru/kvartira/prodazha/2671418111",
        "https://www.realtymag.ru/kvartira/prodazha/2697601084",
        "https://www.realtymag.ru/kvartira/prodazha/2695472584",
        "https://www.realtymag.ru/kvartira/prodazha/2695418404",
        "https://www.realtymag.ru/kvartira/prodazha/2692446279",
        "https://www.realtymag.ru/kvartira/prodazha/2692446276",
        "https://www.realtymag.ru/kvartira/prodazha/2692446274",
        "https://www.realtymag.ru/kvartira/prodazha/2692446262",
        "https://www.realtymag.ru/kvartira/prodazha/2685563458",
        "https://www.realtymag.ru/kvartira/prodazha/2682582427",
        "https://www.realtymag.ru/kvartira/prodazha/2680047426",
        "https://www.realtymag.ru/kvartira/prodazha/2665008005",
        "https://www.realtymag.ru/kvartira/prodazha/2662103971",
        "https://www.realtymag.ru/kvartira/prodazha/2694402942",
        "https://www.realtymag.ru/kvartira/prodazha/2667460262",
        "https://www.realtymag.ru/kvartira/prodazha/2693417531",
        "https://www.realtymag.ru/kvartira/prodazha/2699891020",
        "https://www.realtymag.ru/kvartira/prodazha/2694401886",
    ]

    with open("tests/offers_page.htm", encoding="utf-8") as file:
        html = file.read()
        assert get_links(html) == links_list


def test_get_offers():
    """
    test function return offers data dict
    """
    offer_dict = {
        "live_square": 41.7,
        "microdistrict": "Фрунзенский район",
        "price_per_square": 136691.0,
        "location_lat": 59.8689334,
        "location_long": 30.385426799999998,
        "refresh_time": "46 минут назад",
    }

    with open("tests/offer_data_page.htm", encoding="utf-8") as file:
        html = file.read()
        assert get_offers(html) == offer_dict
