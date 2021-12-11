#! python3  # noqa: E265

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging

# 3rd party library
from scrapy import Spider
from scrapy.http.response import Response
from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings

# project
from geotribu_scraper.items import ArticleItem


# #############################################################################
# ########## Classes ###############
# ##################################
class TutorielsSpider(Spider):
    """Specific spider for tutoriels."""

    settings = get_project_settings()
    name = "geotribu_tutoriels"
    # allowed_domains = ["stackoverflow.com"]
    start_urls = [settings.get("DEFAULT_URL_BASE") + "node/19/"]

    def parse(self, response: Response):
        """Parse URLs.

        :param Response response: HTTP response returned by URL requested
        """
        tutos = Selector(response).css("div.views-row")
        logging.info(
            "La page {} contient {} tutoriels".format(response.url, len(tutos))
        )
        for tuto in tutos:
            # url
            tuto_rel_url = tuto.css("a::attr(href)").get()

            if tuto_rel_url is not None:
                yield response.follow(tuto_rel_url, callback=self.parse_article)

    def parse_article(self, response: Response):
        """Specific parsing logic for Geotribu tutoriels

        :param Response response: HTTP response returned by URL requested
        """
        logging.info(
            "Start parsing ARTICLE: {}".format(response.css("title::text").getall()[0])
        )
        item = ArticleItem()

        # contenu de la art
        art = response.css("article")[0]

        # titre
        art_title_section = art.css("div.title-and-meta")
        art_title = art_title_section.css("h2.node__title a::text").get()
        item["title"] = art_title

        # type d'article - jusqu'en 2013, les revues de presse étaient des tutoriels
        # comme les autres et n'étaient pas aussi structurées
        if "revue de presse" in art_title.lower():
            item["kind"] = "rdp"
        else:
            item["kind"] = "art"

        # url
        art_rel_url = art_title_section.css("h2.node__title a::attr(href)").get()
        item["url_full"] = art_rel_url

        # date de publication
        art_date = art.css("div.date")
        art_date_day = art_date.css("span.day::text").get()
        art_date_month = art_date.css("span.month::text").get()
        art_date_year = art_date.css("span.year::text").get()
        item["published_date"] = (art_date_day, art_date_month, art_date_year)

        # tags
        item["tags"] = art_title_section.css("span.taxonomy-tag a::text").getall()

        # récupération de l'intro
        try:
            item["intro"] = art.css("div.field-name-field-introduction").getall()[0]
        except IndexError:
            logging.debug("Article doesn't have introduction.")
            item["intro"] = None

        # corps
        art_raw_body = art.css("div.field-name-body")
        art_out_body = []
        for el in art_raw_body:
            art_out_body.append(el.get())

        item["body"] = art_out_body

        # images URLS (converted into absolute)
        item["image_urls"] = [
            response.urljoin(i) for i in art.css("img").xpath("@src").getall()
        ]

        # author
        author_block = art.css("div.view.view-about-author")
        if author_block:
            # author thumbnail
            thumbnail = (
                art.css("div.view.view-about-author").css("img").xpath("@src").getall()
            )
            if thumbnail and len(thumbnail):
                thumbnail = (
                    art.css("div.view.view-about-author")
                    .css("img")
                    .xpath("@src")
                    .getall()[0]
                )
            else:
                thumbnail = "?"

            # author name
            name = (
                author_block.css("div.views-field.views-field-field-nom-complet")
                .css("div.field-content::text")
                .getall()
            )
            if name and len(name):
                author_block.css("div.views-field.views-field-field-nom-complet").css(
                    "div.field-content::text"
                ).getall()[0]
            else:
                name = "?"

            item["author"] = {
                "thumbnail": thumbnail,
                "name": name,
                "description": author_block.css(
                    "div.views-field.views-field-field-description p"
                ).getall(),
            }
        else:
            item["author"] = {
                "thumbnail": "?",
                "name": art_title_section.css("span.username a::text").get(),
                "description": "",
            }

        yield item


# #############################################################################
# ##### Main #######################
# ##################################
if __name__ == "__main__":
    pass
