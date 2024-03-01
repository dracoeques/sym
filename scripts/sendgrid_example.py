
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def create_email_template(sender, recipient, subject, content):
    """
    Create a simple email template.
    
    :param sender: Email address of the sender
    :param recipient: Email address of the recipient
    :param subject: Subject of the email
    :param content: Body of the email
    :return: Mail object
    """
    email = Mail(
        from_email=sender,
        to_emails=recipient,
        subject=subject,
        html_content=content
    )
    return email

def send_email(email, sendgrid_api_key):
    """
    Send an email using SendGrid.

    :param email: Mail object
    :param sendgrid_api_key: API key for SendGrid
    """
    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(email)
        print(f"Email sent! Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

def create_article_email_template(sender, recipient, subject, articles):
    html_content = "<html><body>"
    for index, (title, summary, link) in enumerate(articles, start=1):
        html_content += f"<p><strong style='font-size: 16px;'>{index}. {title}</strong><br>{summary} <a href={link}>link</a></p>"
    html_content += "</body></html>"

    email = Mail(
        from_email=sender,
        to_emails=recipient,
        subject=subject,
        html_content=html_content
    )
    return email

# Example usage
if __name__ == "__main__":
    sender = "symprojectai@gmail.com"
    recipient = "blakedallen@gmail.com"
    subject = "Latest Articles"
    articles = [
        ("Article 1 Title", "Summary of article 1", "https://sym.ai/app/ode/10"),
        ("Article 2 Title", "Summary of article 2", "https://sym.ai/app/ode/10"),
        ("Article 3 Title", "Summary of article 3", "https://sym.ai/app/ode/10")
    ]

    email = create_article_email_template(sender, recipient, subject, articles)
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
    send_email(email, sendgrid_api_key)

# # Example usage
# if __name__ == "__main__":
#     # Example data
#     sender = "symprojectai@gmail.com"
#     recipient = "blakedallen@gmail.com"
#     subject = "Hello from SendGrid"
#     content = "<strong>This is a test email sent using SendGrid.</strong>"

#     # Create the email
#     email = create_email_template(sender, recipient, subject, content)

#     # Send the email - Replace 'your_sendgrid_api_key' with your actual SendGrid API key
#     sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
#     send_email(email, sendgrid_api_key)

# # Remember to replace 'your_sendgrid_api_key' with your actual SendGrid API key before running the script.
