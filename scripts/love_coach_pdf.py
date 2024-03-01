

bg_img = "/Users/blakeallen/src/github.com/blakedallen/sym-project/scripts/data/heart_coach_bg.png"

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import Color
from reportlab.lib.colors import blue


# Path to your background image


def draw_background(canvas, doc):
    """
    Draw the background image on the canvas.
    """
    canvas.drawImage(bg_img, 0, 0, width=letter[0], height=letter[1], preserveAspectRatio=True, mask='auto')

# Create the PDF document
doc = SimpleDocTemplate("output.pdf", pagesize=letter)

# Styles for title and text
styles = getSampleStyleSheet()
#title_style = styles['Title']
text_style = styles['BodyText']



# Define a custom pink color
custom_pink = Color(0.88, 0.22, 0.61)  # RGB values between 0 and 1
custom_grey = Color(67.0/255,67.0/255,67.0/255)

font_header = "OutfitBold"
roboto_bold_path = "https://sym-public-assets.s3.us-west-2.amazonaws.com/fonts/Outfit-Bold.ttf"
pdfmetrics.registerFont(TTFont(font_header, roboto_bold_path))

font_body = "OutfitLight"
roboto_light_path = "https://sym-public-assets.s3.us-west-2.amazonaws.com/fonts/Outfit-Light.ttf"
pdfmetrics.registerFont(TTFont(font_body, roboto_light_path))

title_style = ParagraphStyle(
    'TitleStyle',
    fontName='OutfitBold',  # Font type
    fontSize=24,                # Font size
    leading=22,                 # Space between lines
    alignment=TA_CENTER,        # Center alignment
    textColor=custom_pink        # Set the text color to pink
)

h2_style = ParagraphStyle(
    'H2Style',
    fontName='OutfitBold',  # Font type
    fontSize=18,                # Font size
    leading=22,                 # Space between lines
    alignment=TA_CENTER,        # Center alignment
    textColor=custom_grey        # Set the text color
)

h3_style = ParagraphStyle(
    'H3Style',
    fontName='OutfitBold',  # Font type
    fontSize=13,                # Font size
    leading=22,                 # Space between lines
    #alignment=TA_CENTER,        # Center alignment
    textColor=custom_grey        # Set the text color
)


body_style = ParagraphStyle(
    'BodyStyle',
    fontName='OutfitLight',  # Font type
    fontSize=13,                # Font size
    leading=22,                 # Space between lines
    #alignment=TA_CENTER,        # Center alignment
    textColor=custom_grey        # Set the text color
)

# Add a title and some text
story = []
story.append(Paragraph("Your Love Coach Special Report", title_style))
story.append(Spacer(1, 6))
story.append(Paragraph('"The Empathetic Guide"', h2_style))
story.append(Spacer(1, 24))

story.append(Paragraph('What Type of Love Coach am I?', h3_style))
story.append(Spacer(1, 6))

t = """Your love coach type is "The Empathetic Guide." As an Empathetic Guide, you excel at understanding and validating the emotions of your clients. You focus on creating a safe and supportive environment where clients feel comfortable expressing their feelings. This is an essential quality in a love coach, as it helps build trust and openness, allowing clients to delve deeper into their issues. 

Your approach to conflict resolution is also commendable. By seeking to understand both perspectives before taking any action, you ensure that all parties feel heard and understood. This can lead to more effective and sustainable solutions. 

Moreover, your belief in the importance of emotional connection and mutual understanding in maintaining a healthy relationship aligns well with your role as a love coach. These are key aspects of any successful relationship, and your ability to guide your clients in this area will be highly beneficial. 

Lastly, your approach to handling feedback shows your commitment to maintaining a strong client-coach relationship. By reflecting on feedback emotionally and considering its impact on the relationship, you demonstrate a high level of empathy and respect for your clients.

However, while your empathetic and understanding approach is a strength, it's also important to balance this with practical advice and strategies. Not every issue can be resolved solely through empathy and understanding. Sometimes, clients may need more concrete guidance and action steps. Therefore, developing your skills in this area could further enhance your effectiveness as a love coach.

Overall, your empathetic and understanding approach makes you well-suited to the role of a love coach. With some focus on providing practical advice and strategies, you have the potential to be an excellent love coach.
"""

for x in t.split("\n"):
    tx = x.strip()
    if tx:
        story.append(Paragraph(tx, body_style))
        story.append(Spacer(1, 6))

#from reportlab.platypus import Hyperlink

# Create custom styles
styles = getSampleStyleSheet()
link_style = styles['Normal'].clone('LinkStyle')
link_style.textColor = blue
link_style.underline = True

# Add content with hyperlinks
story.append(Paragraph("To learn more about becoming a love & relationship coach, watch our “Become A Successful Relationship Coach” web class to discover how to master relationship coaching & get paid well to do it.", body_style))
hyperlink_text = Paragraph('<link href="http://example.com" color="blue">link to example.com</link>', body_style)

#link = Hyperlink(url="https://www.heartcoach.com/", text="Click here to watch now", fontName='Helvetica', fontSize=12, textColor=blue)
story.append(hyperlink_text)
story.append(Spacer(1, 12))

# Build the document with the background drawing function
doc.build(story, onFirstPage=draw_background, onLaterPages=draw_background)