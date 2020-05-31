#! python3  # noqa: E265

"""Models for scraped items.

    See documentation in:

    https://docs.scrapy.org/en/latest/topics/items.html
"""


from scrapy import Field, Item


class GeoRdpItem(Item):
    title = Field()
    url_full = Field()
    published_date = Field()
    intro = Field()
    news_sections = Field()
    news_details = Field()
    image_urls = Field()


class ArticleItem(Item):
    title = Field()
    url_full = Field()
    published_date = Field()
    author = Field()
    tags = Field()
    kind = Field()
    intro = Field()
    body = Field()
    image_urls = Field()
