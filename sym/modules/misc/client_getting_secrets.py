import json
import re
from io import BytesIO
import boto3
from uuid import uuid4

from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import red, blue, green



from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def client_getting_secrets(text):
    """ 
        1. Parse data in from this form
        2. Generate responses from prompts
        3. Generate pdf and save to s3
        4. Return a downloadable link from s3
    """

    title_img_url = "https://sym-public-assets.s3.us-west-2.amazonaws.com/client-getting-secrets-logo-blue+(1).png"
    title_img_dimensions = (366, 180)
    
    intro = """Welcome to your Custom Client Getting Scripts created specifically for your client conversations!
    Inside this PDF, you'll discover a collection of carefully crafted scripts designed to help you turn casual chats into rewarding coaching relationships that last. 
    These aren't just words on a screen; they're your key to unlocking a higher level of connection and success with your clients. 
    But here's the secret sauce: don't just read them—live them! 
    Commit to practicing these scripts once a day in front of the mirror, allowing the words to become a natural extension of your professional persona. 
    It might feel a bit odd at first, but stick with it.
    Soon, you'll find yourself effortlessly engaging clients with confidence, authenticity, and flow. 
    So go ahead, embrace the journey, and watch as these scripts transform not only your conversations but your entire coaching career. Happy practicing!"""
    
    sections = parse_responses(text)

    #save to s3
    output_stream = BytesIO()

    filepath = generate_pdf(
        title_img_url=title_img_url,
        title_img_dimensions=title_img_dimensions,
        intro=intro,
        sections=sections,
        fh=output_stream,
        save2s3=True,

    )

    return filepath


def parse_responses(blob):
    lines = blob.strip().split("\n")
    sections = []
    current_section = None
    pattern = r'^\d+\.'
    
    for line in lines:
        stripped = line.strip()

        # Check if it's a section name
        if re.match(pattern, stripped):
        #if stripped[1:3] == ". ":
            # If there's a current section being parsed, add it to the sections list
            if current_section:
                sections.append(current_section)

            current_section = {
                'section_name': stripped,
                'items': []
            }
        # Check if it's a subfeature
        elif stripped.startswith("-"):
            if current_section:
                current_section['items'].append(stripped[2:].strip())

    # Append the last section if any
    if current_section:
        sections.append(current_section)

    return sections

def generate_pdf(
        
        sections,
        fh="output.pdf",
        save2s3=False,
        title_img_url=None,
        title_img_dimensions=None,
        title=None,
        intro=None,
    ):
    
    # Register custom fonts
    font_body = "OutfitLight"
    roboto_light_path = "https://sym-public-assets.s3.us-west-2.amazonaws.com/fonts/Outfit-Light.ttf"
    pdfmetrics.registerFont(TTFont(font_body, roboto_light_path))

    font_header = "OutfitBold"
    roboto_bold_path = "https://sym-public-assets.s3.us-west-2.amazonaws.com/fonts/Outfit-Bold.ttf"
    pdfmetrics.registerFont(TTFont(font_header, roboto_bold_path))
    
    doc = SimpleDocTemplate(fh, pagesize=letter)

    # Prepare the story
    story = []

    # Get some sample styles and define our own
    styles = getSampleStyleSheet()
    styleNormal = ParagraphStyle('normalWithCustomFont', parent=styles['Normal'], fontName=font_body)
    styleHeading = ParagraphStyle('headingWithCustomFont', parent=styles['Heading1'], fontName=font_header)
    styleHeading2 = ParagraphStyle('headingWithCustomFont2', parent=styles['Heading2'], fontName=font_header)

    # Add content to the story
    if title_img_url and title_img_dimensions:
        title_img_url = "https://sym-public-assets.s3.us-west-2.amazonaws.com/client-getting-secrets-logo-blue+(1).png"
        img = Image(title_img_url, width=title_img_dimensions[0], height=title_img_dimensions[1])  # You can adjust width and height as needed
        story.append(img)
        story.append(Spacer(1, 8))
    
    if title:
        story.append(Paragraph(title, font_header))
        story.append(Spacer(1, 8))

    if intro:
        intro_sections = intro.split("\n")
        for s in intro_sections:
            story.append(Paragraph(s, styleNormal))
            story.append(Spacer(1, 4))

    story.append(Spacer(1, 12))

    for section in sections:
        if "section_name" in section:
            # Subheader with custom font
            story.append(Paragraph(section["section_name"], styleHeading2))
        
        bullet_point = '\t\u2022 '
        if "items" in section:
            for item in section["items"]:
                story.append(Paragraph(bullet_point+item, styleNormal))
                story.append(Spacer(1, 4))
        story.append(Spacer(1, 12))


    # Build the document
    doc.build(story)

    filename = fh
    if save2s3:
        s3 = boto3.client('s3')
        fh.seek(0)

        uuid = uuid4()
        key = f'client-getting-secrets/client-getting-secrets_{uuid}.pdf'
        filename = f"https://sym-public-assets.s3.us-west-2.amazonaws.com/{key}"
        s3.upload_fileobj(
            Fileobj=fh, 
            Bucket='sym-public-assets',
            Key=key
        )
    return filename
