"""
    Custom pipelines.

    See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
"""

# standard library
import json
import logging
from datetime import datetime
from pathlib import Path

# 3rd party
from markdownify import markdownify as md

# package module
from geotribu_scraper.items import GeoRdpItem
from geotribu_scraper.settings import URLS_BASE_REPLACEMENTS

# #############################################################################
# ########## Globals ###############
# ##################################
# folder_output = Path("_output/" + datetime.now().strftime("%d%m%Y_%H%M"))
folder_output = Path("_output")
folder_output.mkdir(exist_ok=True, parents=True)


# #############################################################################
# ######### Pipelines ##############
# ##################################
class ScrapyCrawlerPipeline(object):
    def _isodate_from_raw_dates(
        self, in_raw_date: str, in_type_date: str = "url"
    ) -> datetime:
        """Parse raw dates scraped from old content and try to return a clean datetime object.

        :param str in_raw_date: raw date to convert
        :param str in_type_date: source of raw date. Defaults to: "url" - optional

        :raises NotImplementedError: if in_type_date is not a valid value

        :return: parsed and converted date
        :rtype: datetime

        :example:

        .. code-block:: python

            _isodate_from_raw_dates(
                in_raw_date="/geotribu_reborn/GeoRDP/20150206",
                in_type_date="url"
                )
            datetime.datetime(2015, 2, 06, 0, 0)
        """
        # try to convert raw date into a datetime
        if in_type_date == "url":
            try:
                splitted_url = in_raw_date.split("/")[-1]
                out_date = datetime.strptime(splitted_url, "%Y%m%d")
                return out_date
            except Exception as err:
                logging.error("Raw date parsing {} failed: {}".format(in_raw_date, err))
                return in_type_date
        else:
            raise NotImplementedError

    def process_item(self, item: GeoRdpItem, spider):

        if isinstance(item, GeoRdpItem):
            rdp_date_raw = item.get("published_date")
            rdp_date_iso_from_url = item.get("url_full")
            logging.info("Processing GeoRDP: {}".format(rdp_date_iso_from_url))

            if isinstance(
                self._isodate_from_raw_dates(rdp_date_iso_from_url), datetime
            ):
                rdp_date_clean = self._isodate_from_raw_dates(
                    rdp_date_iso_from_url, in_type_date="url"
                )
                logging.info("RDP date clean: " + str(rdp_date_clean.isocalendar()))
            else:
                rdp_date_clean = "{} {} {}".format(
                    rdp_date_raw[0], rdp_date_raw[1], rdp_date_raw[2]
                )

    def process_image(self, in_md_str: str):
        for old_url in URLS_BASE_REPLACEMENTS:
            if old_url in in_md_str:
                logging.info("Old URL spotted: {}".format(old_url))
                return in_md_str.replace(old_url, URLS_BASE_REPLACEMENTS.get(old_url))

        return in_md_str

                logging.warning(
                    "Cleaning date failed, using raw date: {}".format(rdp_date_clean)
                )

            # output filename
            if isinstance(rdp_date_clean, str):
                out_file = folder_output / Path("rdp_{}.md".format(rdp_date_clean))
            elif isinstance(rdp_date_clean, datetime):
                out_file = folder_output / Path(
                    "rdp_{}.md".format(rdp_date_clean.strftime("%Y-%m-%d"))
                )
            else:
                pass

            # out_item_md = Path(item.get("title"))
            with out_file.open(mode="w", encoding="UTF8") as out_item_as_md:
                # out_item_as_md.write("# {}".format(item.get("title")))
                out_item_as_md.write(
                    "# {} {}\n\n".format(item.get("title"), rdp_date_clean.year)
                )
                out_item_as_md.write("{}----\n".format(md(item.get("intro"))))

                sections = item.get("news_sections")
                logging.info(
                    "News sections in this RDP: {}".format(" | ".join(sections))
                )

                for k, v in item.get("news_details").items():
                    # insert section
                    out_item_as_md.write("\n## {}\n".format(md(k)))

                    # parse news details
                    for news in v:
                        if news[0]:
                            out_item_as_md.write("### {}\n".format(md(news[0])))
                        if news[1]:
                            out_item_as_md.write(
                                "\n{}{}\n\n".format(
                                    md(news[1]), "{: .img-rdp-news-thumb }"
                                )
                            )

                        out_item_as_md.write(
                            "{}".format("\n".join([md(el) for el in news[2]]))
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
