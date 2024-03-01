import os
import re,json
from uuid import uuid4
import boto3
import requests
from sym.modules.misc.keap_crm import achieve_api_goal, get_contact_id_by_email, create_contact, get_custom_fields, get_custom_field_by_name, assign_custom_field, get_contact
from sym.modules.utils.openaiapi import prompt_openai, prompt_openai_async


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import Color
from reportlab.lib.colors import blue


#if so, just return that rather than building the pdf / running prompts

async def get_love_coach_pdf_url(payload):
    binary_response_str = get_binary_response_string(payload)
    pdffilename = f"love_coach_01_2024_{binary_response_str}.pdf"
    path = f"https://sym-public-assets.s3.us-west-2.amazonaws.com/heart_coach/reports/{pdffilename}"
    return path

async def create_love_coach_pdf(payload, model="gpt-4"):

    email = payload["email"]
    if "model" in payload:
        model = payload["model"]

    #get the results from the payload
    binary_response_str = get_binary_response_string(payload)
    pdffilename = f"love_coach_01_2024_{binary_response_str}.pdf"
    path = f"https://sym-public-assets.s3.us-west-2.amazonaws.com/heart_coach/reports/{pdffilename}"
    cached_report, coach_type = check_cached_response(path, pdffilename)
    if cached_report is not None:
        return {
            "coach_type":coach_type,
            "report_url":cached_report,
            "email":email,
            "model":model,
        }
    
    q1,q2,q3,q4,q5,q6,q7 = unpack_binary_responses(payload)

    #run the prompts
    p1,p2,p3,p4 = await run_prompts(q1,q2,q3,q4,q5,q6,q7, model=model)

    #get the love coach type
    coach_type = extract_love_coach_type(p1)
    #update the coach type so we can use in a cached response
    coach_types = update_love_coach_type(coach_type, pdffilename)

    #generate the pdf
    report_url, report_local_file = create_pdf(p1,p2,p3,p4, love_coach_type=coach_type, save2s3=True, pdffilename=pdffilename)
    #remove the local file
    os.remove(report_local_file)


    #optional - set the custom values for email
    #err = set_contact_values(email, report_url)

    return {
        # "p1":p1,
        # "p2":p2,
        # "p3":p3,
        # "p4":p4,
        "coach_type":coach_type,
        "report_url":report_url,
        "email":email,
        "model":model,
    }


def extract_love_coach_type(text):
    pattern = r"Your love coach type is (.*?)\."
    match = re.search(pattern, text)
    if match:
        return match.group(1).title().replace('"', "")
    else:
        return "Unique Love Coach"


def check_cached_response(path, pdffilename):
    #Just return existing report / coach type if exists
    coach_type = ""
    r = requests.get("https://sym-public-assets.s3.us-west-2.amazonaws.com/heart_coach/coach_types.json")
    coach_types = r.json()
    if pdffilename in coach_types:
        coach_type = coach_types[pdffilename]
    
    r = requests.head(path)
    if r.status_code == requests.codes.ok:
        return path, coach_type
    else:
        return None, None

def update_love_coach_type(coach_type, pdffilename):
    r = requests.get("https://sym-public-assets.s3.us-west-2.amazonaws.com/heart_coach/coach_types.json")
    coach_types = r.json()
    coach_types[pdffilename] = coach_type
    local_filename = "coach_types.json"
    with open(local_filename, "w") as fh:
        fh.write(json.dumps(coach_types))

    s3 = boto3.client('s3')

    key = f'heart_coach/coach_types.json'
    filename = f"https://sym-public-assets.s3.us-west-2.amazonaws.com/{key}"
    s3.upload_file(
        local_filename, 
        Bucket='sym-public-assets',
        Key=key,
        ExtraArgs={'ContentType': 'application/json'}
    )
    os.remove(local_filename)
    return coach_types


def get_binary_response_string(payload):
    return f"""{payload["q1"]},{payload["q2"]},{payload["q3"]},{payload["q4"]},{payload["q5"]},{payload["q6"]},{payload["q7"]}"""

def unpack_binary_responses(payload):
    q_from_binary = {
        "q1":{
            1:"Option 1: Seek to understand both perspectives before taking any action.",
            0:"Option 2: Rely on logical solutions to resolve the issue quickly.",
        },
        "q2":{
            1:"Option 1: Creating a safe and empathetic space for clients to express their feelings.",
            0:"Option 2: Providing direct advice and action steps for clients to follow.",
        },
        "q3":{
            1:"Option 1: Listen intently and validate the other person's feelings.",
            0:"Option 2: Focus on analyzing the facts and finding the root cause of the issue.",
        },
        "q4":{
            1:"Option 1: As a guide who helps clients discover their own solutions to relationship challenges.",
            0:"Option 2: As an expert who imparts knowledge and strategies for successful relationships.",
        },
        "q5":{
            1:"Option 1: Explore various emotional perspectives and the underlying feelings involved.",
            0:"Option 2: Use proven methodologies and techniques to address the issue.",
        },
        "q6":{
            1:"Option 1: Emotional connection and mutual understanding.",
            0:"Option 2: Practical compatibility and shared life goals.",
        },
        "q7":{
            1:"Option 1: Reflect on the feedback emotionally and consider how it affects the client-coach relationship.",
            0:"Option 2: Analyze the feedback objectively to improve coaching techniques and outcomes.",
        }
    }

    q1 = q_from_binary["q1"][payload["q1"]]
    q2 = q_from_binary["q2"][payload["q2"]]
    q3 = q_from_binary["q3"][payload["q3"]]
    q4 = q_from_binary["q4"][payload["q4"]]
    q5 = q_from_binary["q5"][payload["q5"]]
    q6 = q_from_binary["q6"][payload["q6"]]
    q7 = q_from_binary["q7"][payload["q7"]]
    
    return q1,q2,q3,q4,q5,q6,q7

    
    

def set_contact_values(email, report_url):
    payload = {
        "email":email,
    }

    r,err = get_contact_id_by_email(payload)

    contact = None
    if len(r["contacts"]) == 0:
        #Create a new contact
        contact,err = create_contact(payload)
    else:
        contact = r["contacts"][0]
        
    contact_id = contact["id"]

    #get the custom field id for love_coach_report_012024
    field,err = get_custom_field_by_name("love_coach_report_012024")
    
    #r,err = get_custom_fields()
    #print(json.dumps(r, indent=2))

    #set the lovecoach report value for this contact
    cf_payload = {
        "contact_id":contact_id,
        "custom_field_id":field["id"],
        "content":report_url,
    }
    r,err = assign_custom_field(cf_payload)
    

    # #OPTIONAL check contact custom field has been set
    # r, err = get_contact(contact_id)

    # for cf in r["custom_fields"]:
    #     if cf["id"] == field["id"]:
    #         assert cf["content"] == "http://www.lovecoachtest.com/123456.pdf", "Error custom field content does not match expected output"

    


def create_pdf(p1,p2,p3,p4, love_coach_type="", pdffilename=None, save2s3=True):
    bg_img = "https://sym-public-assets.s3.us-west-2.amazonaws.com/heart_coach/heart_coach_bg.png"
    
    def draw_background(canvas, doc):
        """
        Draw the background image on the canvas.
        """
        canvas.drawImage(bg_img, 0, 0, width=letter[0], height=letter[1], preserveAspectRatio=True, mask='auto')


    # Create the PDF document
    if pdffilename is None:
        uuid = uuid4()
        fh = f"love_coach_01_2024_{uuid}.pdf"
    else:
        fh = pdffilename
    doc = SimpleDocTemplate(fh, pagesize=letter)

    # Define custom colors
    custom_pink = Color(0.88, 0.22, 0.61)  # RGB values between 0 and 1
    custom_grey = Color(67.0/255,67.0/255,67.0/255)

    # Register custom fonts
    font_body = "OutfitLight"
    roboto_light_path = "https://sym-public-assets.s3.us-west-2.amazonaws.com/fonts/Outfit-Light.ttf"
    pdfmetrics.registerFont(TTFont(font_body, roboto_light_path))

    font_header = "OutfitBold"
    roboto_bold_path = "https://sym-public-assets.s3.us-west-2.amazonaws.com/fonts/Outfit-Bold.ttf"
    pdfmetrics.registerFont(TTFont(font_header, roboto_bold_path))

    pdfmetrics.registerFont(TTFont("OutfitMedium", "https://sym-public-assets.s3.us-west-2.amazonaws.com/fonts/Outfit-Medium.ttf"))

    title_style = ParagraphStyle(
        'TitleStyle',
        fontName='OutfitMedium',  # Font type
        fontSize=24,                # Font size
        leading=22,                 # Space between lines
        alignment=TA_CENTER,        # Center alignment
        textColor=custom_pink        # Set the text color to pink
    )

    h2_style = ParagraphStyle(
        'H2Style',
        fontName='OutfitMedium',  # Font type
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

    # Prepare the story
    story = []

    story.append(Paragraph("Your Love Coach Special Report", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"{love_coach_type}", h2_style))
    story.append(Spacer(1, 24))

    #P1
    story.append(Paragraph('What Type of Love Coach am I?', h3_style))
    story.append(Spacer(1, 6))

    for x in p1.split("\n"):
        tx = x.strip()
        if tx:
            story.append(Paragraph(tx, body_style))
            story.append(Spacer(1, 6))
    story.append(Spacer(1, 6))

    #P2
    story.append(Paragraph("What are my main strengths & how can I best use them?", h3_style))
    story.append(Spacer(1, 6))

    for x in p2.split("\n"):
        tx = x.strip()
        if tx:
            story.append(Paragraph(tx, body_style))
            story.append(Spacer(1, 6))
    story.append(Spacer(1, 6))

    #P3
    story.append(Paragraph("What are my shadow areas & how can I develop them?", h3_style))
    story.append(Spacer(1, 6))

    for x in p3.split("\n"):
        tx = x.strip()
        if tx:
            story.append(Paragraph(tx, body_style))
            story.append(Spacer(1, 6))
    story.append(Spacer(1, 6))

    #P4
    story.append(Paragraph("My Love Coach Summary", h3_style))
    story.append(Spacer(1, 6))

    for x in p4.split("\n"):
        tx = x.strip()
        if tx:
            story.append(Paragraph(tx, body_style))
            story.append(Spacer(1, 6))
    story.append(Spacer(1, 6))

    story.append(Paragraph("To learn more about becoming a love & relationship coach, watch our “Become A Successful Relationship Coach” web class to discover how to master relationship coaching & get paid well to do it.", body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph('<link href="http://www.heartcoach.com/love-coach/thank-you" color="blue">Click here to watch now.</link>', body_style))
    story.append(Spacer(1, 12))

    # Build the document with the background drawing function
    doc.build(story, onFirstPage=draw_background, onLaterPages=draw_background)

    #save the file to s3
    filename = fh
    if save2s3:
        s3 = boto3.client('s3')
        #fh.seek(0)

        key = f'heart_coach/reports/{fh}'
        filename = f"https://sym-public-assets.s3.us-west-2.amazonaws.com/{key}"
        s3.upload_file(
            fh, 
            Bucket='sym-public-assets',
            Key=key,
            ExtraArgs={'ContentType': 'application/pdf'}
        )
    return filename, fh



async def run_prompts(q1,q2,q3,q4,q5,q6,q7, model="gpt-3.5-turbo"):
    
    p1,_ = await prompt1(q1,q2,q3,q4,q5,q6,q7, model=model)
    p2,_ = await prompt2(q1,q2,q3,q4,q5,q6,q7, model=model)
    p3,_ = await prompt3(q1,q2,q3,q4,q5,q6,q7, model=model)
    p4,_ = await prompt4(q1,q2,q3,q4,q5,q6,q7, model=model)
    return p1,p2,p3,p4


def prompt1(A1,A2,A3,A4,A5,A6,A7, model="gpt-3.5-turbo"):
    p = f"""
        Write a few short paragraphs for a prospective love coach who has just taken a 7-question quiz online about their "love coach type." 
        When creating their love coach type, make sure it's concise and only 1-3 words max. 
        Explain why they would or would not be a good love coach. 
        No preamble. Just go right into the content. 
        Start the paragraph with "Your love coach type is..."

        Here’s the test results in the form of an interview with the person. 

        Questions 1: When faced with a relationship conflict, do you tend to:
        Option 1: Seek to understand both perspectives before taking any action.
        Option 2: Rely on logical solutions to resolve the issue quickly.

        Answer 1: {A1}


        Question 2: When discussing sensitive topics, do you:
        Option 1: Listen intently and validate the other person's feelings.
        Option 2: Focus on analyzing the facts and finding the root cause of the issue.

        Answer 2: {A2}


        Question 3: When discussing sensitive topics, do you:
        Option 1: Listen intently and validate the other person's feelings.
        Option 2: Focus on analyzing the facts and finding the root cause of the issue.

        Answer 3: {A3}


        Question 4: How do you view the role of a love coach?
        Option 1: As a guide who helps clients discover their own solutions to relationship challenges.
        Option 2: As an expert who imparts knowledge and strategies for successful relationships.

        Answer 4: {A4}


        Question 5: When you encounter a complex relationship issue, do you prefer to:
        Option 1: Explore various emotional perspectives and the underlying feelings involved.
        Option 2: Use proven methodologies and techniques to address the issue.

        Answer 5: {A5}


        Question 6: In your opinion, what is more crucial in maintaining a healthy relationship?
        Option 1: Emotional connection and mutual understanding.
        Option 2: Practical compatibility and shared life goals.

        Answer 6: {A6}


        Question 7: How do you handle feedback in a coaching scenario?
        Option 1: Reflect on the feedback emotionally and consider how it affects the client-coach relationship.
        Option 2: Analyze the feedback objectively to improve coaching techniques and outcomes.

        Answer 7: {A7}


    """

    return prompt_openai_async(prompt=p, model=model)

def prompt2(A1,A2,A3,A4,A5,A6,A7, model="gpt-3.5-turbo"):
    p = f"""

        Write a few short paragraphs for a prospective love coach who has just taken a 7-question quiz online about their main strengths to get clients, do a coaching session, create a coaching package, design an initial coaching session, and build credibility. No preamble. Just go right into the content. Start the paragraph with "Your primary strengths as a potential love coach..."

        Here’s the test results in the form of an interview with the person. 

        Questions 1: When faced with a relationship conflict, do you tend to:
        Option 1: Seek to understand both perspectives before taking any action.
        Option 2: Rely on logical solutions to resolve the issue quickly.

        Answer 1: {A1}


        Question 2: When discussing sensitive topics, do you:
        Option 1: Listen intently and validate the other person's feelings.
        Option 2: Focus on analyzing the facts and finding the root cause of the issue.

        Answer 2: {A2}


        Question 3: When discussing sensitive topics, do you:
        Option 1: Listen intently and validate the other person's feelings.
        Option 2: Focus on analyzing the facts and finding the root cause of the issue.

        Answer 3: {A3}


        Question 4: How do you view the role of a love coach?
        Option 1: As a guide who helps clients discover their own solutions to relationship challenges.
        Option 2: As an expert who imparts knowledge and strategies for successful relationships.

        Answer 4: {A4}


        Question 5: When you encounter a complex relationship issue, do you prefer to:
        Option 1: Explore various emotional perspectives and the underlying feelings involved.
        Option 2: Use proven methodologies and techniques to address the issue.

        Answer 5: {A5}


        Question 6: In your opinion, what is more crucial in maintaining a healthy relationship?
        Option 1: Emotional connection and mutual understanding.
        Option 2: Practical compatibility and shared life goals.

        Answer 6: {A6}


        Question 7: How do you handle feedback in a coaching scenario?
        Option 1: Reflect on the feedback emotionally and consider how it affects the client-coach relationship.
        Option 2: Analyze the feedback objectively to improve coaching techniques and outcomes.

        Answer 7: {A7}


    """

    return prompt_openai_async(prompt=p, model=model)

def prompt3(A1,A2,A3,A4,A5,A6,A7, model="gpt-3.5-turbo"):
    p = f"""
        Write a few short paragraphs for a prospective love coach who has just taken a 7-question quiz online about their main shadow areas and how to overcome them. No preamble. Just go right into the content. Start the paragraph with "Your shadow areas as a love coach..."

        Here’s the test results in the form of an interview with the person. 

        Questions 1: When faced with a relationship conflict, do you tend to:
        Option 1: Seek to understand both perspectives before taking any action.
        Option 2: Rely on logical solutions to resolve the issue quickly.

        Answer 1: {A1}


        Question 2: When discussing sensitive topics, do you:
        Option 1: Listen intently and validate the other person's feelings.
        Option 2: Focus on analyzing the facts and finding the root cause of the issue.

        Answer 2: {A2}


        Question 3: When discussing sensitive topics, do you:
        Option 1: Listen intently and validate the other person's feelings.
        Option 2: Focus on analyzing the facts and finding the root cause of the issue.

        Answer 3: {A3}


        Question 4: How do you view the role of a love coach?
        Option 1: As a guide who helps clients discover their own solutions to relationship challenges.
        Option 2: As an expert who imparts knowledge and strategies for successful relationships.

        Answer 4: {A4}


        Question 5: When you encounter a complex relationship issue, do you prefer to:
        Option 1: Explore various emotional perspectives and the underlying feelings involved.
        Option 2: Use proven methodologies and techniques to address the issue.

        Answer 5: {A5}


        Question 6: In your opinion, what is more crucial in maintaining a healthy relationship?
        Option 1: Emotional connection and mutual understanding.
        Option 2: Practical compatibility and shared life goals.

        Answer 6: {A6}


        Question 7: How do you handle feedback in a coaching scenario?
        Option 1: Reflect on the feedback emotionally and consider how it affects the client-coach relationship.
        Option 2: Analyze the feedback objectively to improve coaching techniques and outcomes.

        Answer 7: {A7}


    """

    return prompt_openai_async(prompt=p, model=model)

def prompt4(A1,A2,A3,A4,A5,A6,A7, model="gpt-3.5-turbo"):
    p = f"""
        Write a summary for a prospective love coach who has just taken a 7-question quiz online. Write in a few short paragraphs. No preamble. Just go right into the content. Start the paragraph with "To summarize..."

        Here’s the test results in the form of an interview with the person. 

        Questions 1: When faced with a relationship conflict, do you tend to:
        Option 1: Seek to understand both perspectives before taking any action.
        Option 2: Rely on logical solutions to resolve the issue quickly.

        Answer 1: {A1}


        Question 2: When discussing sensitive topics, do you:
        Option 1: Listen intently and validate the other person's feelings.
        Option 2: Focus on analyzing the facts and finding the root cause of the issue.

        Answer 2: {A2}


        Question 3: When discussing sensitive topics, do you:
        Option 1: Listen intently and validate the other person's feelings.
        Option 2: Focus on analyzing the facts and finding the root cause of the issue.

        Answer 3: {A3}


        Question 4: How do you view the role of a love coach?
        Option 1: As a guide who helps clients discover their own solutions to relationship challenges.
        Option 2: As an expert who imparts knowledge and strategies for successful relationships.

        Answer 4: {A4}


        Question 5: When you encounter a complex relationship issue, do you prefer to:
        Option 1: Explore various emotional perspectives and the underlying feelings involved.
        Option 2: Use proven methodologies and techniques to address the issue.

        Answer 5: {A5}


        Question 6: In your opinion, what is more crucial in maintaining a healthy relationship?
        Option 1: Emotional connection and mutual understanding.
        Option 2: Practical compatibility and shared life goals.

        Answer 6: {A6}


        Question 7: How do you handle feedback in a coaching scenario?
        Option 1: Reflect on the feedback emotionally and consider how it affects the client-coach relationship.
        Option 2: Analyze the feedback objectively to improve coaching techniques and outcomes.

        Answer 7: {A7}


    """

    return prompt_openai_async(prompt=p, model=model)

