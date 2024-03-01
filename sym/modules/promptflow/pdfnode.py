from dataclasses import dataclass, field


from sym.modules.misc.client_getting_secrets import client_getting_secrets

import asyncio, threading

@dataclass
class PdfNode:
  id: str = None
  node_type: str = "pdf"
  finished: bool = False

  logo_image_url: str = ""

  intro_text: str = ""
  intro_title: str = ""

  outro_title: str = ""
  outro_text: str = ""



  async def run(self, payload=None):

    #check for variables
    #TODO: intro_text outro text etc. 


    #

    #yield the pdf url
    yield None, True