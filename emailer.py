import re
import smtplib
import markdown
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL, PASSWORD, SMTP_SERVER, SMTP_PORT

def send_email(issue):
    repo_name = issue["repository_url"].split("/")[-1]
    subject = f"New Issue in {repo_name}: {issue['title']}"
    title = issue["title"]
    raw_body = issue["body"] or "No description provided."
    body_html = markdown.markdown(raw_body)
    url = issue["html_url"]

    body_html = re.sub(
        r'<img(.*?)>',
        r'<img\1 style="max-width:100%; height:auto; display:block; margin:0 auto; margin-bottom:5px;">',
        body_html
    )

    html_body = f"""
    <html>
    <body style="margin: 0; padding: 0; background-color: #f4f4f7; font-family: 'Segoe UI', sans-serif;">
        <div style="max-width: 750px; margin: 40px auto; background-color: white; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); overflow: hidden;">
            <div style="background-color: #24292e; padding: 24px; text-align: center;">
                <h1 style="color: white; margin: 0 auto; font-size: 22px; display: inline-block;">{title}</h1>
            </div>
            <div style="padding: 32px; text-align: center;">
                <div style="font-size: 12px; color: #555555; text-align: left; line-height: 1.5;">
                    <style>
                        h1 {{
                            font-size: 16px;
                            margin-top: 0;
                            margin-bottom: 10px;
                        }}
                        h2 {{
                            font-size: 14px;
                            margin-top: 0;
                            margin-bottom: 8px;
                        }}
                        h3 {{
                            font-size: 12px;
                            margin-top: 0;
                            margin-bottom: 6px;
                        }}
                        p {{
                            font-size: 12px;
                            line-height: 1.5;
                            color: #555555;
                            margin-bottom: 15px;
                        }}
                    </style>
                    {body_html}
                </div>
                <div style="margin-top: 30px;">
                    <a href="{url}" style="background-color: #2ea44f; color: white; padding: 12px 20px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                        View Issue on GitHub
                    </a>
                </div>
            </div>
            <div style="padding: 16px; text-align: center; background-color: #f9f9f9; font-size: 12px; color: #888888;">
                Powered by <strong>GitSignal</strong>
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL
    msg["To"] = EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, EMAIL, msg.as_string())
        print("Email sent.")
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False
