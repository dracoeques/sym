from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import red, blue, green

c = canvas.Canvas("output.pdf", pagesize=letter)
width, height = letter
roboto_light_path = "/Users/blakedallen/go/src/github.com/blakedallen/sym-project/scripts/Roboto/Roboto-Light.ttf"

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register a TTF font
font_name = "CustomFont"
pdfmetrics.registerFont(TTFont(font_name, roboto_light_path))

# Header
c.setFont("Helvetica-Bold", 24)
c.drawString(100, height - 100, "My Custom PDF")

# Subheader with custom font
c.setFont(font_name, 18)
c.drawString(100, height - 150, "Using Custom Font")

# Colored Text
c.setFillColor(red)
c.setFont("Times-Roman", 12)
c.drawString(100, height - 200, "This is a red text!")

c.setFillColor(blue)
c.drawString(100, height - 225, "This is a blue text!")

c.setFillColor(green)
c.drawString(100, height - 250, "This is a green text!")

c.save()


