#! python3  # noqa: E265

"""
    Custom pipelines.

    See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
"""

# standard library
import json
import locale
import logging
from datetime import datetime
from pathlib import Path
from typing import Union

# 3rd party
import httpx
from markdownify import markdownify as md
from scrapy import Item, Spider

# package module
from geotribu_scraper.items import ArticleItem, GeoRdpItem
from geotribu_scraper.replacers import URLS_BASE_REPLACEMENTS

# #############################################################################
# ########## Globals ###############
# ##################################
# folder_output = Path("_output/" + datetime.now().strftime("%d%m%Y_%H%M"))
folder_output = Path("_output")
folder_output.mkdir(exist_ok=True, parents=True)

# matching matrix between non standardized dates in Drupal and Python ISO months name
MONTHS_NAMES_MATRIX = {
    "jan": "janv.",
    "fév": "févr.",
    "mar": "mars",
    "avr": "avr.",
    "mai": "mai",
    "juin": "juin",
    "juil": "juil.",
    "aoû": "août",
    "sep": "sept.",
    "oct": "oct.",
    "nov": "nov.",
    "déc": "déc.",
}


# #############################################################################
# ######### Pipelines ##############
# ##################################
class ScrapyCrawlerPipeline(object):
    @staticmethod
    def check_url(url: str) -> bool:
        with httpx.Client() as client:
            r = client.get(url)

        logging.debug("URL checked: {} - {}".format(url, r.status_code))

        return r

    def _isodate_from_raw_dates(
        self, in_raw_date: str, in_type_date: str = "url"
    ) -> datetime:
        """Parse raw dates scraped from old content and try to return a clean datetime object.

        :param str in_raw_date: raw date to convert
        :param str in_type_date: source of raw date: 'url' or 'date_tag'.\
             Defaults to: "url" - optional

        :raises NotImplementedError: if in_type_date is not a valid value

        :return: parsed and converted date
        :rtype: datetime

        :example:

        .. code-block:: python

            # recent RDP got their date in URL
            _isodate_from_raw_dates(
                in_raw_date="/geotribu_reborn/Article/20150206",
                in_type_date="url"
                )
            datetime.datetime(2015, 2, 06, 0, 0)

            # older got only in a (non standardized) date tag which is
            #  retrieved by spider as a tuple
            _isodate_from_raw_dates(
                in_raw_date=("20", "avr", "2014"),
                in_type_date="date_tag"
                )
            datetime.datetime(2015, 2, 06, 0, 0)
        """
        self._locale_setter(expected_locale="fr_FR")

        # try to convert raw date into a datetime
        if in_type_date == "url":
            try:
                splitted_url = in_raw_date.split("/")[-1]
                out_date = datetime.strptime(splitted_url, "%Y%m%d")
                logging.debug("Raw date converted from URL format: {}".format(out_date))
                return out_date
            except Exception as err:
                logging.debug("Raw date parsing {} failed: {}".format(in_raw_date, err))
                return in_type_date
        elif in_type_date == "date_tag" and isinstance(in_raw_date, tuple):
            # use matrix to get a standardiez month value
            month_standard = MONTHS_NAMES_MATRIX.get(in_raw_date[1].lower())
            date_as_str = "{0[0]} {1} {0[2]}".format(in_raw_date, month_standard)
            try:
                out_date = datetime.strptime(date_as_str, "%d %b %Y")
                logging.debug(
                    "Raw date converted from date tags format: {}".format(out_date)
                )
                return out_date
            except Exception as err:
                logging.debug("Raw date parsing {} failed: {}".format(in_raw_date, err))
                return in_type_date
        else:
            raise NotImplementedError

    @staticmethod
    def _locale_setter(expected_locale: str = "fr_FR"):
        """Ensure locale is the expected one."""
        # get the default locale on system
        default_locale = locale.getdefaultlocale()  # -> tuple

        # compare with the expected locale
        if default_locale[0] == expected_locale:
            logging.debug(
                "Default locale is matching the expected one: {}".format(
                    expected_locale
                )
            )
            locale.setlocale(locale.LC_ALL, "")
        else:
            logging.warning(
                "Default locale ({}) is not the expected one: {}. "
                "Change will be effective until the end of program.".format(
                    default_locale, expected_locale
                )
            )
            locale.setlocale(locale.LC_ALL, expected_locale)

    def process_content(self, in_md_str: str) -> str:
        """Check images in content and try to replace broken paths using a dict (stored in settings).

        :param str in_md_str: markdown content

        :return: markdown content with images paths replaced
        :rtype: str
        """
        for old_url in URLS_BASE_REPLACEMENTS:
            if old_url in in_md_str:
                logging.debug("Old URL spotted: {}".format(old_url))

                # new_url = URLS_BASE_REPLACEMENTS.get(old_url)

                # # check if new url will work
                # r = self.check_url(new_url)
                # # if r.is_error:
                # if r.status_code >= 400:
                #     logging.error("Image new URL is not correct: {}".format(new_url))

                return in_md_str.replace(old_url, URLS_BASE_REPLACEMENTS.get(old_url))

        return in_md_str.strip(" \t")

    @staticmethod
    def title_builder(
        raw_title: str,
        append_year_at_end: bool = True,
        item_date_clean: Union[datetime, str] = None,
    ) -> str:
        """Handy method to build a clean title.

        :param str raw_title: scraped title
        :param bool append_year_at_end: option to append year at the end of title. Defaults to: True - optional
        :param Union[datetime, str] item_date_clean: cleaned date of the item

        :return: clean title ready to be written into a markdown file
        :rtype: str
        """
        if append_year_at_end:
            # extract year from date
            if isinstance(item_date_clean, datetime):
                year = str(item_date_clean.year)
            else:
                year = str(item_date_clean.split("-")[2])

            # append year only if not already present in title
            if year not in raw_title:
                out_title = "{} {}".format(raw_title, year)
            else:
                out_title = raw_title
        else:
            out_title = raw_title.strip()

        logging.debug("Title: %s" % out_title)
        return "# {}\n\n".format(out_title.strip())

    @staticmethod
    def process_images_links(li_images_urls: list):
        for old_url in URLS_BASE_REPLACEMENTS:
            if old_url in li_images_urls:
                for img_old_url in li_images_urls:
                    new_url = img_old_url.replace(
                        old_url, URLS_BASE_REPLACEMENTS.get(old_url)
                    )

        yield new_url

    def process_item(self, item: Item, spider: Spider) -> Item:
        """Process each item output by a spider. It performs these steps:

            1. Extract date handling different formats
            2. Use it to format output filename
            3. Convert content into a markdown file handling different cases

        :param GeoRdpItem item: output item to process
        :param Spider spider: [description]

        :return: item passed
        :rtype: Item
        """

        if isinstance(item, GeoRdpItem):
            logging.debug(
                "Processing Article located at this URL: {}".format(
                    item.get("url_full")
                )
            )

            # try to get a clean date from scraped raw ones
            rdp_date_raw = self._isodate_from_raw_dates(
                item.get("published_date"), in_type_date="date_tag"
            )
            rdp_date_iso_from_url = self._isodate_from_raw_dates(
                item.get("url_full"), in_type_date="url"
            )

            if isinstance(rdp_date_raw, datetime):
                rdp_date_clean = rdp_date_raw
                logging.debug(
                    "Using date tag as clean date: {}".format(
                        rdp_date_clean.isocalendar()
                    )
                )
            elif isinstance(rdp_date_iso_from_url, datetime):
                rdp_date_clean = rdp_date_iso_from_url
                logging.debug(
                    "Using date from url as clean date: {}".format(
                        rdp_date_clean.isocalendar()
                    )
                )
            else:
                rdp_date_clean = "{0[2]}-{0[1]}-{0[0]}".format(
                    item.get("published_date")
                ).lower()
                logging.warning(
                    "Cleaning date failed, using raw date: {}".format(rdp_date_clean)
                )

            # output filename
            if isinstance(rdp_date_clean, datetime):
                out_file = folder_output / Path(
                    "rdp_{}.md".format(rdp_date_clean.strftime("%Y-%m-%d"))
                )
            else:
                out_file = folder_output / Path("rdp_{}.md".format(rdp_date_clean))

            # out_item_md = Path(item.get("title"))
            with out_file.open(mode="w", encoding="UTF8") as out_item_as_md:
                # write RDP title
                out_item_as_md.write(
                    self.title_builder(
                        raw_title=item.get("title"), item_date_clean=rdp_date_clean
                    )
                )

                # introduction
                intro_clean_img = self.process_content(md(item.get("intro")))
                out_item_as_md.write("{}----\n".format(intro_clean_img))

                sections = item.get("news_sections")
                logging.debug(
                    "News sections in this RDP: {}".format(" | ".join(sections))
                )

                for k, v in item.get("news_details").items():
                    # insert section
                    out_item_as_md.write("\n## {}\n".format(md(k)))

                    # parse news details
                    for news in v:
                        # news title
                        if news[0]:
                            out_item_as_md.write("### {}\n".format(md(news[0])))

                        # news thumbnail
                        if news[1]:
                            img_clean = self.process_content(md(news[1]))
                            out_item_as_md.write(
                                "\n{}{}\n\n".format(
                                    img_clean, "{: .img-rdp-news-thumb }"
                                )
                            )

                        # news content
                        for element in news[2]:
                            # exception for iframes
                            if element.startswith("<iframe "):
                                news_detail_img_clean = "{}\n".format(element)
                            else:
                                news_detail_img_clean = self.process_content(
                                    md(element, strip=["iframe"])
                                )

                            out_item_as_md.write("{}\n".format(news_detail_img_clean))

            return item
        elif isinstance(item, ArticleItem):
            logging.debug(
                "Processing Article located at this URL: {}".format(
                    item.get("url_full")
                )
            )

            # try to get a clean date from scraped raw ones
            art_date_raw = self._isodate_from_raw_dates(
                item.get("published_date"), in_type_date="date_tag"
            )
            art_date_iso_from_url = self._isodate_from_raw_dates(
                item.get("url_full"), in_type_date="url"
            )

            if isinstance(art_date_raw, datetime):
                art_date_clean = art_date_raw
                logging.debug(
                    "Using date tag as clean date: {}".format(
                        art_date_clean.isocalendar()
                    )
                )
            elif isinstance(art_date_iso_from_url, datetime):
                art_date_clean = art_date_iso_from_url
                logging.debug(
                    "Using date from url as clean date: {}".format(
                        art_date_clean.isocalendar()
                    )
                )
            else:
                art_date_clean = "{0[2]}-{0[1]}-{0[0]}".format(
                    item.get("published_date")
                ).lower()
                logging.warning(
                    "Cleaning date failed, using raw date: {}".format(art_date_clean)
                )

            # output filename
            if isinstance(art_date_clean, datetime):
                out_file = folder_output / Path(
                    "{}_{}.md".format(
                        item.get("kind"), art_date_clean.strftime("%Y-%m-%d")
                    )
                )
            else:
                out_file = folder_output / Path(
                    "{}_{}.md".format(item.get("kind"), art_date_clean)
                )

            #

            # out_item_md = Path(item.get("title"))
            with out_file.open(mode="w", encoding="UTF8") as out_item_as_md:
                if item.get("kind") == "art":
                    category_long = "article"
                else:
                    category_long = "GeoRDP"

                # write YAMl front-matter
                yaml_frontmatter = (
                    '---\ntitle: "{}"\nauthors: {}\n'
                    "category: {}\ndate: {}\ntags: {}\n---\n\n".format(
                        item.get("title"),
                        md(item.get("author").get("name")),
                        category_long,
                        art_date_clean.strftime("%Y-%m-%d"),
                        " | ".join(item.get("tags")),
                    )
                )

                out_item_as_md.write(yaml_frontmatter)

                # write RDP title
                if item.get("kind") == "rdp":
                    out_item_as_md.write(
                        self.title_builder(
                            raw_title=item.get("title"),
                            item_date_clean=art_date_clean,
                            append_year_at_end=True,
                        )
                    )
                else:
                    out_item_as_md.write(
                        self.title_builder(
                            raw_title=item.get("title"),
                            item_date_clean=art_date_clean,
                            append_year_at_end=False,
                        )
                    )

                # date de publication
                out_item_as_md.write(
                    "\n:calendar: Date de publication initiale : {}\n".format(
                        art_date_clean.strftime("%d %B %Y")
                    )
                )

                # mots-clés
                out_item_as_md.write(
                    "\n**Mots-clés :** {}\n\n".format(
                        " | ".join(item.get("tags")).strip()
                    )
                )

                # introduction
                if item.get("intro"):
                    intro_clean = self.process_content(md(item.get("intro")))
                    out_item_as_md.write("{}\n\n----\n".format(intro_clean.strip()))

                # corps
                for element in item.get("body"):
                    # exception for iframes
                    if element.startswith("<iframe "):
                        body_element_clean = "\n{}\n".format(element)
                    else:
                        body_element_clean = self.process_content(
                            md(element, heading_style="ATX")
                        )

                    body_element_clean = body_element_clean.strip(" ").lstrip("\t")
                    out_item_as_md.write("\n{}\n".format(body_element_clean))

                # author
                if item.get("kind") != "rdp":
                    author = item.get("author")
                    out_item_as_md.write("\n----\n\n## Auteur\n\n")

                    # clean thumbnail url
                    thumb_url = author.get("thumbnail").split("?")[0]

                    # write output
                    img_clean = self.process_content(thumb_url)
                    out_item_as_md.write(
                        "![Portait de {}]({}){}\n".format(
                            md(author.get("name")),
                            md(img_clean),
                            "{: .img-rdp-news-thumb }",
                        )
                    )
                    out_item_as_md.write(
                        "**{}**\n\n".format(
                            self.process_content(md(author.get("name")))
                        )
                    )

                    for author_d in author.get("description"):
                        out_item_as_md.write(
                            "{}".format(self.process_content(md(author_d)))
                        )

            return item


class JsonWriterPipeline(object):
    def open_spider(self, spider):
        out_filename = folder_output / Path("items.jl")
        self.file = out_filename.open(mode="w", encoding="UTF8")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
