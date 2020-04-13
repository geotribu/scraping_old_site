#! python3  # noqa: E265

import logging

from scrapy import Spider
from scrapy.selector import Selector

from geotribu_scraper.items import ArticleItem
from geotribu_scraper.spiders.rdp_crawler import GeoRDPSpider


class ArticlesSpider(Spider):
    name = "geotribu_articles"
    # allowed_domains = ["stackoverflow.com"]
    start_urls = [
        "http://localhost/geotribu_reborn/articles-blogs",
    ]

    def parse(self, response):
        arts = Selector(response).css("article")
        logging.info("La page {} contient {} articles".format(response.url, len(arts)))
        for art in arts:
            # title
            art_title_section = art.css("div.title-and-meta")

            # url
            art_rel_url = art_title_section.css("h2.node__title a::attr(href)").get()

            if art_rel_url is not None:
                yield response.follow(art_rel_url, callback=self.parse_article)

        # get next page from bottom pagination to iterate over pages
        next_page = response.css("li.pager-next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
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
            logging.error("Article doesn't have introduction.")
            item["intro"] = ""

        # corps
        art_raw_body = art.css("div.field-name-body").getall()
        art_out_body = []
        for el in art_raw_body:
            art_out_body.append(el)

        item["body"] = art_out_body

        # images URLS (converted into absolute)
        item["image_urls"] = [
            response.urljoin(i) for i in art.css("img").xpath("@src").getall()
        ]

        # author
        author_block = art.css("div.view.view-about-author")
        item["author"] = {
            "thumbnail": art.css("div.view.view-about-author")
            .css("img")
            .xpath("@src")
            .getall()[0],
            "name": author_block.css("div.views-field.views-field-field-nom-complet")
            .css("div.field-content::text")
            .getall()[0],
            "description": author_block.css(
                "div.views-field.views-field-field-description p"
            ).getall(),
        }

        yield item
