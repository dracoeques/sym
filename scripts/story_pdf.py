from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register a custom font
font_body = "RobotoLight"
roboto_light_path = "/Users/blakedallen/go/src/github.com/blakedallen/sym-project/scripts/Roboto/Roboto-Light.ttf"
pdfmetrics.registerFont(TTFont(font_body, roboto_light_path))

font_header = "RobotoBold"
roboto_bold_path = "/Users/blakedallen/go/src/github.com/blakedallen/sym-project/scripts/Roboto/Roboto-Bold.ttf"
pdfmetrics.registerFont(TTFont(font_header, roboto_bold_path))

# Create a new document
doc = SimpleDocTemplate("output.pdf", pagesize=letter)

# Prepare the story
story = []

# Get some sample styles and define our own
styles = getSampleStyleSheet()
styleNormal = ParagraphStyle('normalWithCustomFont', parent=styles['Normal'], fontName=font_body)
styleHeading = ParagraphStyle('headingWithCustomFont', parent=styles['Heading1'], fontName=font_header)

# Add content to the story
story.append(Paragraph("1. Section Name", styleHeading))
story.append(Paragraph("This is a very long text for subfeature 1, which will automatically wrap onto the next line as required." * 5, styleNormal))
story.append(Spacer(1, 12))
story.append(Paragraph("2. Another Section", styleHeading))
story.append(Paragraph("This is another long text for subfeature N." * 10, styleNormal))

# Build the document
doc.build(story)
