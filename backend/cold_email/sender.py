import csv
import smtplib
import ssl
import time
import os
import re
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

def extract_email(text):
    if text is None:
        return None
    text = str(text)
    if "Apply via link" in text or "LinkedIn DM" in text:
        return None
    emails = re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text)
    if not emails:
        return None
    return emails[0].strip().lower()

def load_recruiters(csv_file):
    required_columns = {"Company Name", "HR / Contact Person", "Email ID"}
    recruiters = []
    seen_emails = set()

    with open(csv_file, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        missing_columns = required_columns - set(reader.fieldnames or [])
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Recruiter CSV is missing required column(s): {missing}")

        for row in reader:
            email = extract_email(row.get("Email ID"))
            if not email or email in seen_emails:
                continue
            seen_emails.add(email)
            recruiters.append({
                "Company Name": (row.get("Company Name") or "").strip(),
                "HR / Contact Person": (row.get("HR / Contact Person") or "").strip(),
                "Email ID": email,
            })

    return recruiters

def generate_email_body(hr_name, company_name, resume_skills=[]):
    skills_str = ", ".join(resume_skills) if resume_skills else "Python, Machine Learning, Deep Learning, NLP, Data Analysis"
    body = f"""Hi {hr_name},

I came across opportunities at {company_name} and would like to express my interest in AI/ML Engineer, Data Scientist, Machine Learning Engineer, Generative AI, NLP, or related roles.

I am Neha Bharti, a B.Tech graduate (2022-2026) with hands-on experience in Artificial Intelligence and Machine Learning. I have worked as an AI/ML Intern at Capsitech IT Services Limited, Jodhpur for 11 months, where I worked on real-world AI projects involving Machine Learning, Deep Learning, NLP, Data Annotation, Prompt Engineering, and Python-based development.

Technical Skills:
{skills_str}

Key Projects:
- AI Recruitment Copilot - AI-powered resume analyzer with ATS scoring, semantic similarity, RAG architecture
- Credit-Risk-Intelligence-Platform
- Modular Training Pipelines

I am currently looking for Full-Time, Internship, or Entry-Level opportunities in AI, Machine Learning, Data Science, NLP, and Generative AI domains.

I have attached my resume for your review. I would be grateful for an opportunity to discuss how my skills can contribute to your team.

Thank you for your time and consideration.

Best Regards,
Neha Bharti
Phone: +91 9608690934
Email: nehab3099@gmail.com
LinkedIn: https://linkedin.com/in/neha-bharti-61956b348
GitHub: https://github.com/NehaBharti16
"""
    return body

def send_cold_emails(csv_path, resume_path, sender_email, app_password, resume_skills=[], delay=30):
    recruiters = load_recruiters(csv_path)
    results = []
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, app_password)

        for row in recruiters:
            hr_name = str(row["HR / Contact Person"]).strip()
            company_name = str(row["Company Name"]).strip()
            receiver_email = str(row["Email ID"]).strip()

            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = receiver_email
            msg["Subject"] = "Application for AI/ML Engineer | Machine Learning | Deep Learning | NLP"

            body = generate_email_body(hr_name, company_name, resume_skills)
            msg.attach(MIMEText(body, "plain"))

            with open(resume_path, "rb") as f:
                attachment = MIMEApplication(f.read(), Name=os.path.basename(resume_path))
            attachment["Content-Disposition"] = f'attachment; filename="{os.path.basename(resume_path)}"'
            msg.attach(attachment)

            try:
                server.send_message(msg)
                results.append({
                    "hr_name": hr_name,
                    "company": company_name,
                    "email": receiver_email,
                    "status": "✅ Sent"
                })
                time.sleep(delay)
            except Exception as e:
                results.append({
                    "hr_name": hr_name,
                    "company": company_name,
                    "email": receiver_email,
                    "status": f"❌ Failed: {str(e)}"
                })

    return results, len(recruiters)
