from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import red, blue, green
import json
import re
from io import BytesIO
import boto3
from uuid import uuid4


from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


# Register custom fonts
font_body = "OutfitLight"
roboto_light_path = "https://sym-public-assets.s3.us-west-2.amazonaws.com/fonts/Outfit-Light.ttf"
pdfmetrics.registerFont(TTFont(font_body, roboto_light_path))

font_header = "OutfitBold"
roboto_bold_path = "https://sym-public-assets.s3.us-west-2.amazonaws.com/fonts/Outfit-Bold.ttf"
pdfmetrics.registerFont(TTFont(font_header, roboto_bold_path))

example = """
1. Qualifying Clients:\n- On a scale of 1-10, how motivated are you to achieve strategic logical improvements through meditative rock climbing?\n- Are you willing to invest yourself in engaging physical wellness and stress alleviation?\n- Are you open to receiving coaching to overcome the challenges you face as a high-level corporate personnel?\n- Are you willing to invest financially to achieve your goals in both your personal and professional life?\n\n2. Transitioning to Offering Coaching Packages:\n- Based on what you told me, the next step is for you to sign up for "The Ultimate Zen Ascent: Strategic Rock Climbing Retreatment for the Exhausted Executive".\n\n3. Building Trust and Qualifying:\n- What are the other problems that engaging physical wellness and stress alleviation could help solve in your life?\n- What are the other results that achieving strategic logical improvements through meditative rock climbing will give you in both your personal and professional life?\n\n4. Content Creation and Invitations:\n- And if you want my personalized digital guide to High-Power Meditative Techniques for stress-alleviating rock climbing, complete with a private interactive coaching session over Zoom uncovering potential physical wellness improvements, just send me an email.\n- If you\'re really serious about engaging physical wellness and stress alleviation through meditative rock climbing, just reach out to me.\n\n5. Offering Support and Help:\n- Let\'s do a call and I\'ll help you make a plan to achieve strategic logical improvements through meditative rock climbing.\n- I\'m here to help you overcome the challenges you face as a high-level corporate personnel.\n\n6. Emphasizing Value and Results:\n- Over the next 90 days, you\'ll achieve strategic logical improvements, engage in physical wellness, and alleviate stress through meditative rock climbing.\n- If you want to get great results, faster results, if you want to accelerate your success in engaging physical wellness and stress alleviation through meditative rock climbing, reach out to me.\n\n7. Reassuring Prospective Clients:\n- This is not a pitch for my coaching. I\'m here to help you overcome the challenges you face as a high-level corporate personnel.\n\n8. Expressing Gratitude:\n- I appreciate your time and consideration in this process. I believe in your potential and I\'m excited about the possibility of helping you reach strategic logical improvements, engage in physical wellness, and alleviate stress through meditative rock climbing.\n\n9. Incorporating Storytelling:\n- Let me share a story about a high-level corporate personnel I worked with who faced similar challenges to the ones you\'re experiencing. Through meditative rock climbing, he was able to achieve strategic logical improvements, engage in physical wellness, and alleviate stress in his life.\n\n10. Identifying Money Making Opportunities:\n- Based on our conversation, I believe there are untapped opportunities that can help you accelerate your success in your personal and professional life through meditative rock climbing.\n11. Highlight Your Value and Results:\n- Over the past 12 innovative and challenging years, I\'ve helped high-level corporate personnel achieve engaging physical wellness and stress alleviation through my meditative rock climbing coaching. Clients have experienced strategic logical improvements in their professional lives as a result.\n\n12. Asking for Referrals:\n- Who else do you know in high-level corporate positions that would like to achieve engaging physical wellness and stress alleviation through meditative rock climbing? \n- Can you think of any high-level executives in your network who might also benefit from "The Ultimate Zen Ascent: Strategic Rock Climbing Retreatment for the Exhausted Executive"?\n\n13. Emphasize Your Expertise and Experience:\n- As a coach with 12 innovative and challenging years of experience and expertise in meditative rock climbing coaching for high-level corporate personnel, I have refined my methods and strategies to deliver even greater results.\n\n14. Communicate the Benefits of Investing in Higher-Level Coaching:\n- By investing in "The Ultimate Zen Ascent," you will receive personalized attention, advanced strategies, and a deeper level of support tailored to high-level corporate personnel. This will enable you to achieve engaging physical wellness and stress alleviation for strategic logical improvements faster and more effectively.\n\n15. Offer a Limited-Time Promotion:\n- For a limited time, I am offering a special promotion where you can lock in "The Ultimate Zen Ascent: Strategic Rock Climbing Retreatment for the Exhausted Executive" at a discounted rate. However, please note that prices for this exclusive coaching package will be increasing in the near future, so now is the best time to take advantage of this opportunity.\n\n16. Provide Testimonials and Social Proof:\n- Many high-level corporate personnel have experienced significant transformations and achieved remarkable results in engaging physical wellness and stress alleviation through "The Ultimate Zen Ascent: Strategic Rock Climbing Retreatment for the Exhausted Executive."\n\n17. Ensuring Comfortable Conversations: \n- I greatly value our coaching relationship and your trust in me. If you know any high-level corporate personnel who could benefit from a similar experience in engaging physical wellness and stress alleviation for strategic logical improvements, would you feel comfortable recommending my services?\n\n18. Offering Special Incentives: \n- As a thank you for your referral, I\'m offering a special discount on your next coaching session for high-level corporate personnel seeking to achieve engaging physical wellness and stress alleviation for strategic logical improvements.\n\n19. Encouraging Ongoing Referrals: \n- Your referral is the highest compliment you can give me. If you know any other high-level corporate executives who could benefit from "The Ultimate Zen Ascent: Strategic Rock Climbing Retreatment for the Exhausted Executive" down the line, please don\'t hesitate to connect them with me.\n\n20. Expressing Gratitude for Referrals: \n- I want to express my deepest gratitude for your willingness to refer my coaching services to other high-level corporate personnel. Your support is invaluable in helping me reach and impact more lives in engaging physical wellness and stress alleviation for strategic logical improvements.
"""

def make_pdf(sections, title="Client Getting Secrets", fh="output.pdf", save2s3=False):

    # Create a new document

    doc = SimpleDocTemplate(fh, pagesize=letter)

    # Prepare the story
    story = []

    # Get some sample styles and define our own
    styles = getSampleStyleSheet()
    styleNormal = ParagraphStyle('normalWithCustomFont', parent=styles['Normal'], fontName=font_body)
    styleHeading = ParagraphStyle('headingWithCustomFont', parent=styles['Heading1'], fontName=font_header)
    styleHeading2 = ParagraphStyle('headingWithCustomFont2', parent=styles['Heading2'], fontName=font_header)

    # Add content to the story
    
    title_img_url = "https://sym-public-assets.s3.us-west-2.amazonaws.com/client-getting-secrets-logo-blue+(1).png"
    img = Image(title_img_url, width=366, height=180)  # You can adjust width and height as needed
    story.append(img)
    #story.append(Paragraph(title, styleHeading))
    story.append(Spacer(1, 8))

    intro = """Welcome to your Custom Client Getting Scripts created specifically for your client conversations!
    Inside this PDF, you'll discover a collection of carefully crafted scripts designed to help you turn casual chats into rewarding coaching relationships that last. 
    These aren't just words on a screen; they're your key to unlocking a higher level of connection and success with your clients. 
    But here's the secret sauce: don't just read them—live them! 
    Commit to practicing these scripts once a day in front of the mirror, allowing the words to become a natural extension of your professional persona. 
    It might feel a bit odd at first, but stick with it.
    Soon, you'll find yourself effortlessly engaging clients with confidence, authenticity, and flow. 
    So go ahead, embrace the journey, and watch as these scripts transform not only your conversations but your entire coaching career. Happy practicing!"""
    
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

    if save2s3:
        s3 = boto3.client('s3')
        fh.seek(0)

        uuid = uuid4()

        s3.upload_fileobj(
            Fileobj=fh, 
            Bucket='sym-public-assets',
            Key=f'client-getting-secrets/client-getting-secrets_{uuid}.pdf'
        )



def parse_text(blob):
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


    



#print(json.dumps(parse_text(example), indent=2))

sections = parse_text(example)

print(json.dumps(sections, indent=2))

make_pdf(sections)
output_stream = BytesIO()
make_pdf(sections, fh=output_stream, save2s3=True)