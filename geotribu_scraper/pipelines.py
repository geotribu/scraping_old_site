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

# 3rd party
from markdownify import markdownify as md
from scrapy import Item, Spider

# package module
from geotribu_scraper.items import GeoRdpItem

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

URLS_BASE_REPLACEMENTS = {
    # -- Custom images -- Default news icon
    "http://localhost/sites/default/public/public_res/default_images/News.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/News_0.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/News_1.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/News_2.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/News_3.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/News_4.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/News_5.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/News_6.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/News_7.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    # -- Custom images -- Default world icon
    "http://localhost/sites/default/public/public_res/default_images/world.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/world_0.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/world_1.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/world_2.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/world_3.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/world_4.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/world_5.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    # generic
    "http://localhost/sites/default/public/public_res/": "https://cdn.geotribu.fr/img/",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/img/": "https://cdn.geotribu.fr/img/",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/default_images/": "https://cdn.geotribu.fr/img/",
    "http://geotribu.net/sites/default/public/public_res/img/": "https://cdn.geotribu.fr/img/",
    "http://www.geotribu.net/sites/default/public/public_res/img/": "https://cdn.geotribu.fr/img/",
}


# #############################################################################
# ######### Pipelines ##############
# ##################################
class ScrapyCrawlerPipeline(object):


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
                in_raw_date="/geotribu_reborn/GeoRDP/20150206",
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
                logging.warning(
                    "Raw date parsing {} failed: {}".format(in_raw_date, err)
                )
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
                logging.warning(
                    "Raw date parsing {} failed: {}".format(in_raw_date, err)
                )
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

    def process_image(self, in_md_str: str):
        for old_url in URLS_BASE_REPLACEMENTS:
            if old_url in in_md_str:
                logging.info("Old URL spotted: {}".format(old_url))
                return in_md_str.replace(old_url, URLS_BASE_REPLACEMENTS.get(old_url))

        return in_md_str

    @staticmethod
    def title_builder(raw_title: str, item_date_clean: Union[datetime, str]) -> str:
        """Handy method to build a clean title.

        :param str raw_title: scraped title
        :param Union[datetime, str] item_date_clean: cleaned date of the item

        :return: clean title ready to be written into a markdown file
        :rtype: str
        """
        # extract year from date
        if isinstance(item_date_clean, datetime):
            year = item_date_clean.year
        else:
            year = item_date_clean.split("-")[2]

        # append year only if not already present in title
        out_title = raw_title + " " + year

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

    def process_item(self, item: Item, spider: Spider) -> Item:
        """Process each item output by a spider. It performs these steps:

            1. Extract date handling different formats
            2. Use it to format output filename
            3. Convert content into a markdown file handling different cases

        :param GeoRdpItem item: output item to process
        :param Spider spider: [description]

        :return: item passed
        :rtype: Item

        :example:

        .. code-block:: python

            # here comes an example in Python
        """

        if isinstance(item, GeoRdpItem):
            logging.info(
                "Processing GeoRDP located at this URL: {}".format(item.get("url_full"))
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
                logging.info(
                    "Using date tag as clean date: ".format(
                        rdp_date_clean.isocalendar()
                    )
                )
            elif isinstance(rdp_date_iso_from_url, datetime):
                rdp_date_clean = rdp_date_iso_from_url
                logging.info(
                    "Using date from url as clean date: ".format(
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
                logging.info(
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
                            news_detail_img_clean = self.process_content(md(element))
                            out_item_as_md.write("{}\n".format(news_detail_img_clean))

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
