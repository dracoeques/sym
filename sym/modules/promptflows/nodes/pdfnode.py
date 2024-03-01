from dataclasses import dataclass, field
from typing import List
from sym.modules.promptflows.nodes.core import PromptNode, PromptEdge

from sym.modules.db.models import Node as NodeRecord
from sym.modules.db.models import Edge as EdgeRecord


import json
import re
from io import BytesIO
import boto3
from uuid import uuid4

import os

from jinja2 import Environment, BaseLoader


#from pyhtml2pdf import converter
import pdfkit



@dataclass
class PDFNode(PromptNode):

    id: int = None
    node_type: str = "pdf"

    #custom values unique to this node
    html_text: str = "" #pdf is converted from html
    s3_bucket: str = "sym-public-assets"
    s3_folder: str = "misc"
    s3_key: str = None #generated via uuid


    async def run(self, input_payload=None, **kwargs):
        
        print("input_to_pdf", json.dumps(input_payload, indent=2))

        #create the pdf, 
        jinja_env = Environment(loader=BaseLoader)
        html_template = jinja_env.from_string(self.html_text)
        if input_payload is None:
            input_payload = {}
        generated_html = html_template.render(input_payload)
        
        # create a temp html file, convert to pdf
        uuid = uuid4()
        html_temp_path = f"tempfile_{uuid}.html"
        pdf_temp_path = f"tempfile_{uuid}.pdf"
        with open(html_temp_path, "wb") as fp:
            fp.write(bytes(generated_html, "utf-8"))
            fp.close()
            path = os.path.abspath(html_temp_path)
            print(path)
            pdfkit.from_file(f'{path}', pdf_temp_path) 
            #converter.convert(f'file://{path}', pdf_temp_path)
        
        # upload to s3
        if self.s3_key is None:
            self.s3_key = f'{self.s3_folder}/{uuid}.pdf'
        
    
        s3 = boto3.client('s3')
        s3.upload_file(
            pdf_temp_path, 
            self.s3_bucket, 
            self.s3_key, 
            ExtraArgs={'ContentType': 'application/pdf'})
          


        # delete temp files
        os.remove(html_temp_path)
        os.remove(pdf_temp_path)

        
        d = self.generate_output_payload(input_payload=input_payload)
        self.output_payload = d
        yield d
    
    def from_node_record(self, r):
        print(r.payload)
        self.id = r.id
        payload = r.payload
        if payload:
            self.input_payload = payload
            if "html_text" in payload:
                self.html_text = payload["html_text"]
        return self
    
    def generate_output_payload(self, input_payload=None):            
        # return url of pdf
        pdf_url = f"https://{self.s3_bucket}.s3.us-west-2.amazonaws.com/{self.s3_key}"
        d = {
            "message":f"Your PDF is ready for download: [{pdf_url}]({pdf_url})",
            "node_data":{
                "id":self.id,
                "node_type":self.node_type,
            },
            "payload":{
                "pdf_url":pdf_url,
            },
            
        }
        return d