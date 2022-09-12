#! python3  # noqa: E265

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging

# 3rd party library
from scrapy import Spider
from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings

# project
from geotribu_scraper.items import GeoRdpItem


# #############################################################################
# ########## Classes ###############
# ##################################
class GeoRDPSpider(Spider):
    """Specific spider for revues de presse."""

    settings = get_project_settings()
    name = "geotribu_rdp"
    # allowed_domains = ["stackoverflow.com"]
    start_urls = [
        settings.get("DEFAULT_URL_BASE") + "revues-de-presse",
    ]

    def parse(self, response):
        rdps = Selector(response).css("article")
        logging.info(
            "La page {} contient {} revues de presse".format(response.url, len(rdps))
        )
        for rdp in rdps:
            # title
            rdp_title_section = rdp.css("div.title-and-meta")

            # url
            rdp_rel_url = rdp_title_section.css("h2.node__title a::attr(href)").get()

            if rdp_rel_url is not None:
                yield response.follow(rdp_rel_url, callback=self.parse_rdp)

        # get next page from bottom pagination to iterate over pages
        next_page = response.css("li.pager-next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_rdp(self, response):
        logging.info(
            "Start parsing RDP: {}".format(response.css("title::text").getall()[0])
        )
        item = GeoRdpItem()

        # contenu de la rdp
        rdp = response.css("article")[0]

        # titre
        rdp_title_section = rdp.css("div.title-and-meta")
        rdp_title = rdp_title_section.css("h2.node__title a::text").get()
        item["title"] = rdp_title

        # type d'article - jusqu'en 2013, les revues de presse étaient des articles
        # comme les autres et n'étaient pas aussi structurées
        if "revue de presse" in rdp_title.lower():
            item["kind"] = "rdp"
        else:
            item["kind"] = "art"

        # url - ne contient pas forcément l'identifiant du noeud de contenu Drupal.
        # Par ex les contenus avec URL personnalisée : /geotribu_reborn/GeoRDP/20150220
        rdp_rel_url = rdp_title_section.css("h2.node__title a::attr(href)").get()
        item["url_full"] = rdp_rel_url

        # shortlink - lien court contenant l'identifiant du noeud de contenu Drupal
        shortlink = response.xpath('//link[@rel="shortlink"]')
        if shortlink:
            short_url_content = shortlink.attrib.get("href")
            if "node" in short_url_content:
                item["drupal_node"] = int(short_url_content.split("/")[-1])

        # date de publication
        rdp_date = rdp.css("div.date")
        rdp_date_day = rdp_date.css("span.day::text").get()
        rdp_date_month = rdp_date.css("span.month::text").get()
        rdp_date_year = rdp_date.css("span.year::text").get()
        item["published_date"] = (rdp_date_day, rdp_date_month, rdp_date_year)

        # tags
        item["tags"] = rdp_title_section.css("span.taxonomy-tag a::text").getall()

        # récupération de l'intro
        intro = ""
        for i in rdp.css("p"):
            if not i.css("p.directNews"):
                intro += i.get()
            else:
                break
        item["intro"] = intro

        # sections
        item["news_sections"] = rdp.css("p.typeNews::text").getall()

        # images URLS (converted into absolute)
        item["image_urls"] = [
            response.urljoin(i) for i in rdp.css("img").xpath("@src").getall()
        ]

        # news
        dico_news_by_section = {}
        start_section = "Non classés"
        for i in rdp.css("div.news-details, p.typeNews"):
            if i.css("p.typeNews"):
                logging.info("Section spotted: {}".format(i.get()))
                active_section = i.get()
                dico_news_by_section.setdefault(active_section, [])
            elif i.css("div.news-details"):
                dico_news_by_section.get(active_section).append(
                    (
                        i.css("span.news-title::text").get(),
                        i.css("img").get(),
                        i.css("p, iframe, li").getall(),
                    )
                )
            else:
                dico_news_by_section.get(start_section).append(i.get())

        item["news_details"] = dico_news_by_section

        # pseudo author to fit others crawlers structure
        item["author"] = {
            "thumbnail": "?",
            "name": "Geotribu",
            "description": "",
        }

        yield item


# #############################################################################
# ##### Main #######################
# ##################################
if __name__ == "__main__":
    pass
