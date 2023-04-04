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
from os import path
from pathlib import Path
from typing import Union

# 3rd party
import httpx
from markdownify import markdownify as md
from scrapy import Item, Request, Spider
from scrapy.pipelines.images import ImagesPipeline
from slugify import slugify
from yaml import safe_dump

# package module
from geotribu_scraper.items import ArticleItem, GeoRdpItem
from geotribu_scraper.replacers import AUTHORS_QUADRIGRAMME, URLS_BASE_REPLACEMENTS

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
    MAPPING_REDIRECTIONS: list = []

    def close_spider(self, spider):
        """This method is called when the spider is closed.

        :param spider: _description_
        :type spider: _type_
        """
        out_filename = folder_output / Path(f"redirection_mapping_{spider.name}.txt")
        with out_filename.open(mode="w", encoding="UTF8") as fifi:
            for pair_url_redirection in self.MAPPING_REDIRECTIONS:
                fifi.write(pair_url_redirection.replace("\\", "/"))

    @staticmethod
    def check_url(url: str) -> bool:
        with httpx.Client() as client:
            r = client.get(url)

        logging.debug("URL checked: {} - {}".format(url, r.status_code))

        return r

    def _extract_node_from_url(self, input_url: str) -> int:
        """Extract Drupal content node id from URL. Used to map legacy URL to the new
        one.

        :param input_url: content URL
        :type input_url: str
        :return: node id
        :rtype: int
        """
        if "node" and "/" in input_url:
            node_id = input_url.split("/")[-1]
            if node_id.isdigit():
                return int(node_id)

        return None

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

    def yaml_frontmatter_as_str(
        self,
        author: str,
        category: str,
        in_date: datetime,
        introduction: str,
        legacy_content_node: int,
        tags: list,
        title: str,
    ) -> str:
        """Build and return YAML FrontMatter.

        :param author: author name
        :type author: str
        :param category: content category
        :type category: str
        :param in_date: content date
        :type in_date: datetime
        :param introduction: content introduction
        :type introduction: str
        :param legacy_content_node: legacy content node
        :type legacy_content_node: int
        :param tags: list of content keywords
        :type tags: list
        :param title: content title
        :type title: str

        :return: YAML frontmatter ready to be written
        :rtype: str
        """
        if category == "GeoRDP":
            category = [
                "revue de presse",
            ]
        else:
            category = [
                "article",
            ]

        description = "{}...".format(introduction[:160])

        dico_frontmatter = {
            "authors": [author],
            "categories": category,
            "date": "{} 10:20".format(in_date.strftime("%Y-%m-%d")),
            "description": description,
            "image": "",
            "license": "default",
            "legacy": {"node": legacy_content_node},
            "robots": "index, follow",
            "tags": tags,
            "title": title,
        }

        return safe_dump(
            data=dico_frontmatter,
            allow_unicode=True,
            # default_style='"',
            explicit_start=True,
            # explicit_end="---",
            indent=4,
            width=1000,
        )

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
        :param Spider spider: Scrapy spider which is used

        :return: item passed
        :rtype: Item
        """
        # -- Common

        # category
        if item.get("kind") in ("art", "tuto"):
            category_long = "articles"
        else:
            category_long = "rdp"

        # date
        # try to get a clean date from scraped raw ones
        item_date_raw = self._isodate_from_raw_dates(
            item.get("published_date"), in_type_date="date_tag"
        )
        item_date_iso_from_url = self._isodate_from_raw_dates(
            item.get("url_full"), in_type_date="url"
        )

        if not item.get("drupal_node"):
            item_legacy_node = self._extract_node_from_url(
                input_url=item.get("url_full")
            )
        else:
            item_legacy_node = item.get("drupal_node")

        if isinstance(item_date_raw, datetime):
            item_date_clean = item_date_raw
            logging.debug(
                "Using date tag as clean date: {}".format(item_date_clean.isocalendar())
            )
        elif isinstance(item_date_iso_from_url, datetime):
            item_date_clean = item_date_iso_from_url
            logging.debug(
                "Using date from url as clean date: {}".format(
                    item_date_clean.isocalendar()
                )
            )
        else:
            item_date_clean = "{0[2]}-{0[1]}-{0[0]}".format(
                item.get("published_date")
            ).lower()
            logging.warning(
                "Cleaning date failed, using raw date: {}".format(item_date_clean)
            )

        # filepath
        if isinstance(item_date_clean, datetime):
            if category_long != "rdp":
                out_file = folder_output / Path(
                    "{}/{}/{}_{}.md".format(
                        category_long,
                        item_date_clean.strftime("%Y"),
                        item_date_clean.strftime("%Y-%m-%d"),
                        slugify(
                            item.get("title"),
                            separator="_",
                            stopwords=["du", "dans", "le", "la"],
                        ),
                    )
                )
            else:
                out_file = folder_output / Path(
                    "{}/{}/rdp_{}.md".format(
                        category_long,
                        item_date_clean.strftime("%Y"),
                        item_date_clean.strftime("%Y-%m-%d"),
                    )
                )
        else:
            out_file = folder_output / Path(
                "{}_{}.md".format(item.get("kind"), item_date_clean)
            )

        out_file.parent.mkdir(parents=True, exist_ok=True)

        # add URLS to redirections mapping
        self.MAPPING_REDIRECTIONS.append(
            f'"node/{item_legacy_node}.md": "/{out_file.relative_to(folder_output)}"\n'
        )

        # introduction
        if item.get("intro"):
            intro_clean = self.process_content(md(item.get("intro")))
        else:
            intro_clean = ""

        # Author
        author = item.get("author")

        # YAML front-matter
        yaml_frontmatter = self.yaml_frontmatter_as_str(
            author=author.get("name"),
            category=category_long,
            introduction=intro_clean,
            title=item.get("title"),
            in_date=item_date_clean,
            tags=item.get("tags"),
            legacy_content_node=item_legacy_node,
        )

        # -- Specific
        if isinstance(item, GeoRdpItem):
            logging.debug(
                "Processing GeoRDP located at this URL: {}".format(item.get("url_full"))
            )

            # out_item_md = Path(item.get("title"))
            with out_file.open(mode="w", encoding="UTF8") as out_item_as_md:
                # write YAMl front-matter
                out_item_as_md.write(yaml_frontmatter)
                out_item_as_md.write("---\n\n")

                # write RDP title
                out_item_as_md.write(
                    self.title_builder(
                        raw_title=item.get("title"), item_date_clean=item_date_clean
                    )
                )

                # date de publication
                out_item_as_md.write(
                    ":calendar: Date de publication initiale : {}\n".format(
                        item_date_clean.strftime("%d %B %Y")
                    )
                )

                # introduction
                out_item_as_md.write("\n{}----\n".format(intro_clean))

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

            # out_item_md = Path(item.get("title"))
            with out_file.open(mode="w", encoding="UTF8") as out_item_as_md:
                if item.get("kind") == "art":
                    category_long = "articles"
                else:
                    category_long = "rdp"

                # write YAMl front-matter
                out_item_as_md.write(yaml_frontmatter)
                out_item_as_md.write("---\n\n")

                # write title
                if item.get("kind") == "rdp":
                    out_item_as_md.write(
                        self.title_builder(
                            raw_title=item.get("title"),
                            item_date_clean=item_date_clean,
                            append_year_at_end=True,
                        )
                    )
                else:
                    out_item_as_md.write(
                        self.title_builder(
                            raw_title=item.get("title"),
                            item_date_clean=item_date_clean,
                            append_year_at_end=False,
                        )
                    )

                # date de publication
                out_item_as_md.write(
                    "\n:calendar: Date de publication initiale : {}\n".format(
                        item_date_clean.strftime("%d %B %Y")
                    )
                )

                # mots-clés
                # out_item_as_md.write(
                #     "\n**Mots-clés :** {}\n\n".format(
                #         " | ".join(item.get("tags")).strip()
                #     )
                # )

                # introduction
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

                    final_body_txt = ""
                    for lili in body_element_clean.splitlines():
                        final_body_txt += lili.lstrip()
                        final_body_txt += "\n"
                    out_item_as_md.write("\n{}\n".format(final_body_txt))

                # author
                if item.get("kind") != "rdp":
                    out_item_as_md.write("\n----\n\n## Auteur\n\n")

                    if author.get("name").lower() in AUTHORS_QUADRIGRAMME:
                        out_item_as_md.write(
                            '--8<-- "{}"\n'.format(
                                AUTHORS_QUADRIGRAMME.get(author.get("name").lower())
                            )
                        )
                    else:
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


class CustomImagesPipeline(ImagesPipeline):
    """Customize how images are downloaded. Stores images \
    into a subfolder named `full` under the path defined in setting `IMAGES_STORE`.\

    Inherits from ImagesPipeline, the generic images pipelines from Scrapy. \
    See: <https://doc.scrapy.org/en/latest/topics/media-pipeline.html?#using-the-images-pipeline>
    """

    # Name download version
    def file_path(self, request, response=None, info=None) -> str:
        """Output image path.

        :param [type] request: [description]
        :param [type] response: [description]. Defaults to: None - optional
        :param [type] info: [description]. Defaults to: None - optional


        :return: path and filename
        :rtype: str
        """
        # item=request.meta['item'] # Like this you can use all from item, not just url.
        # image_guid = request.url.split("/")[-1]
        image_name = request.url.split("/")[-1]
        return "full/%s" % (image_name)

    # Name thumbnail version
    def thumb_path(self, request, thumb_id, response=None, info=None) -> str:
        """Output thumbnails path.

        :param [type] request: [description]
        :param [type] thumb_id: [description]
        :param [type] response: [description]. Defaults to: None - optional
        :param [type] info: [description]. Defaults to: None - optional


        :return: path and filename
        :rtype: str
        """
        image_guid = thumb_id + request.url.split("/")[-1]
        return "thumbs/%s/%s.jpg" % (thumb_id, image_guid)

    def get_media_requests(self, item, info):
        """Retrieve meta from request

        :param [type] item: [description]
        :param [type] info: [description]
        """
        if "images" in item:
            for image_url, img_name in item["images"].iteritems():
                if not path.exists(path.join(item["images_path"], img_name)):
                    request = Request(url=image_url)
                    request.meta["img_name"] = img_name
                    request.meta["this_prod_img_folder"] = item["img_name_here"]
                    request.dont_filter = True
                    yield request
