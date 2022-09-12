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
    author = Field()
    intro = Field()
    tags = Field()
    kind = Field()
    news_sections = Field()
    news_details = Field()
    # media pipelines
    image_urls = Field()
    images = Field()
    # legacy
    drupal_node = Field()


class ArticleItem(Item):
    title = Field()
    url_full = Field()
    published_date = Field()
    author = Field()
    tags = Field()
    kind = Field()
    intro = Field()
    body = Field()
    # media pipelines
    image_urls = Field()
    images = Field()
    # legacy
    drupal_node = Field()
