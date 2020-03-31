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
    def process_item(self, item: GeoRdpItem, spider):
        # output filename
        out_file = folder_output / Path("{}.md".format(item.get("title")))

        # out_item_md = Path(item.get("title"))
        with out_file.open(mode="w", encoding="UTF8") as out_item_as_md:
            # out_item_as_md.write("# {}".format(item.get("title")))
            out_item_as_md.write("# {} \n\n".format(item.get("title")))
            out_item_as_md.write("{}\n\n----\n\n".format(md(item.get("intro"))))

        return item


class JsonWriterPipeline(object):
    def open_spider(self, spider):
        self.file = open("items.jl", "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
