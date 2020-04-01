# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


def serialize_title(value, as_syntax: str = "markdown"):
    if as_syntax == "markdown":
        return "# {} \n\n".format(value)
    else:
        raise NotImplemented


class GeoRdpItem(Item):
    title = Field(serializer=serialize_title)
    url_full = Field()
    published_date = Field()
    intro = Field()
    news_sections = Field()
    news_details = Field()

    @property
    def title_as_markdown(self) -> str:
        return "# {} \n\n".format(self.title)
