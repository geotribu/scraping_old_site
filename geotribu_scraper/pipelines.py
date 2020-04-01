"""
    Custom pipelines.

    See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
"""

# standard library
import json
from datetime import datetime
from pathlib import Path

# 3rd party
from markdownify import markdownify as md

# package module
from geotribu_scraper.items import GeoRdpItem


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
        """[summary]

        :param list in_dates: [description]


        :return: [description]
        :rtype: datetime

        :example:

        .. code-block:: python

            # here comes an example in Python
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



class JsonWriterPipeline(object):
    def open_spider(self, spider):
        self.file = open("items.jl", "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
