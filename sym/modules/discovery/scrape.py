from typing import List
from dataclass import dataclass


@dataclass
class Scraper:

    session = None
    source_url: str = None
    urls:list[str] = None

    def run(self):
        """ """
        pass