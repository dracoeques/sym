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

from sym.modules.promptflows.nodes.pdfnode import PDFSection


sections = [
    PDFSection(
        section_type="title+text",
        title="Overview",
        body="""From your responses, it's clear that you're passionate about your coaching business and have a strong desire to succeed. However, you're also facing a common challenge - the fear of success. This fear is evident in the feelings of confusion and overwhelm you experience when thinking about achieving your dream or goal. It seems that you're uncertain about how to start and are apprehensive about the increased workload and responsibility that success might bring. The good news is that these feelings are normal and can be managed with the right strategies and mindset. """
    ),
    PDFSection(
        section_type="title+text",
        title="Understanding Your Fear of Success",
        body="""From your responses, it's clear that you're passionate about your coaching business and have a strong desire to succeed. However, you're also facing a common challenge - the fear of success. This fear is evident in the feelings of confusion and overwhelm you experience when thinking about achieving your dream or goal. It seems that you're uncertain about how to start and are apprehensive about the increased workload and responsibility that success might bring. The good news is that these feelings are normal and can be managed with the right strategies and mindset. """
    ),
    PDFSection(
        section_type="title+text",
        title="Action Plan",
        body="""To overcome your fear of success, it's important to start by acknowledging your fears and understanding that they're a normal part of the journey towards success. Cognitive Behavioral Therapy (CBT) can be a helpful tool for this. CBT involves identifying negative thought patterns and replacing them with more positive and realistic thoughts. In your case, this might involve challenging thoughts like "I'll be too busy if I succeed" or "I don't know where to start."\n\nNext, consider setting smaller, achievable goals to help you start your project. This can help reduce feelings of overwhelm and make the task seem more manageable. For example, you might start by creating a simple outline for your coaching program or writing a single blog post for your website.\n\nAffirmations and mantras can also be a powerful tool for overcoming fear and cultivating a positive mindset. You might choose a mantra like "I am capable of handling success" or "I am ready to take the next step towards my goal."\n\nImproving your self-esteem can also help you overcome your fear of success. This might involve recognizing your past achievements, focusing on your strengths, and challenging negative self-talk. Mindfulness and meditation can also be helpful for reducing anxiety and promoting a positive mindset.\n\nFinally, consider seeking support from others. This might involve finding a mentor, joining a support group for entrepreneurs, or simply talking to friends and family about your fears. A supportive environment can provide encouragement, advice, and a safe space for you to express your fears and concerns.\n\nRemember, overcoming the fear of success is a journey, not a destination. Be patient with yourself and celebrate your progress along the way. With time, patience, and the right strategies, you can overcome your fear of success and achieve your goals."""
    ),
]


def render(sections, save2s3=True):
    """ 
        1. Parse data in from this form
        2. Generate responses from prompts
        3. Generate pdf and save to s3
        4. Return a downloadable link from s3
    """

    title_img_url = "https://assets-global.website-files.com/64ee39d44b81a0ec6c03c3ba/64fb3e3c08df437b20722a4c_SC%20logo%2018-p-500.png"
    title_img_dimensions = (432, 74)
    
    intro = """"""
    
    #sections = parse_responses(text)

    #save to s3
    output_stream = BytesIO()

    filepath = generate_pdf(
        title_img_url=title_img_url,
        title_img_dimensions=title_img_dimensions,
        intro=intro,
        sections=sections,
        fh=output_stream,
        save2s3=save2s3,

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
        title_img_url = "https://sym-public-assets.s3.us-west-2.amazonaws.com/prompt-flow-assets/46/Screenshot+2023-11-27+at+12.36.02+PM.png"
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

        if section.section_type == "title+bullets":
            if section.title:
                # Subheader with custom font
                story.append(Paragraph(section.title, styleHeading2))
            
            bullet_point = '\t\u2022 '
            if section.items:
                for item in section.items:
                    story.append(Paragraph(bullet_point+item, styleNormal))
                    story.append(Spacer(1, 4))
            story.append(Spacer(1, 12))
        elif section.section_type == "title+text":
            if section.title:
                # Subheader with custom font
                story.append(Paragraph(section.title, styleHeading2))
            
            if section.body:
                for block in section.body.split("\n"):
                    if block:
                        story.append(Paragraph(block, styleNormal))
                        story.append(Spacer(1, 6))
            
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


if __name__ == "__main__":

    filepath = render(sections, save2s3=True)
    print(filepath)