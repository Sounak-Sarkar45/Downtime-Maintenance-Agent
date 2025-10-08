import smtplib
from email.mime.text import MIMEText

def send_shortfall_email(shortfall_df, sender_email, sender_password, receiver_email):
    """
    Sends an email alert if a production shortfall is detected.
    """
    shortfall_detected = shortfall_df['Shortfall'].any()
    if not shortfall_detected:
        print("No production shortfall detected. No email will be sent.")
        return

    email_body = "Production Shortfall Alert\n\n"
    email_body += "The Production Shortfall Forecaster has identified potential underproduction for the upcoming month(s).\n\n"

    for index, row in shortfall_df.iterrows():
        if row['Shortfall']:
            email_body += (
                f"For the month of {row['Month']}:\n"
                f"- Forecasted Total Units: {row['Forecasted Total Units']:.2f}\n"
                f"- Monthly Target: {row['Monthly Target']:.2f}\n"
                f"- Shortfall Detected: YES\n\n"
            )

    msg = MIMEText(email_body)
    msg['Subject'] = "Production Shortfall Alert"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Shortfall email alert sent successfully.")
    except Exception as e:
        print(f"Failed to send shortfall email: {e}")


def send_risk_summary_email(risk_scores_df, sender_email, sender_password, receiver_email):
    """
    Sends an email alert summarizing location-wise risks.
    """
    high_risk_locations = risk_scores_df[risk_scores_df['Risk Tier'] == 'High']
    if high_risk_locations.empty:
        print("No high-risk locations detected. No location risk email will be sent.")
        return

    email_body = "Location Risk Summary Alert\n\n"
    email_body += "The Location Risk Classifier has identified the following high-risk facilities:\n\n"

    for index, row in high_risk_locations.iterrows():
        email_body += (
            f"Location: {row['CITY']}, {row['COUNTRY']}\n"
            f"- Predicted Risk Score: {row['Average_Risk_Score']:.2f}\n"
            f"- Risk Tier: {row['Risk Tier']}\n\n"
        )
    
    msg = MIMEText(email_body)
    msg['Subject'] = "High-Risk Location Alert"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Location risk summary email sent successfully.")
    except Exception as e:
        print(f"Failed to send risk summary email: {e}")


def send_safety_email(safety_scores_df, sender_email, sender_password, receiver_email):
    """
    Sends an email alert for high-risk locations based on safety metrics.
    """
    high_risk_locations = safety_scores_df[safety_scores_df['Safety_Risk_Tier'] == 'High']
    if high_risk_locations.empty:
        print("No high-risk locations based on safety were detected. No safety email will be sent.")
        return

    email_body = "Safety and Continuity Alert\n\n"
    email_body += "The Safety and Continuity Agent has identified the following facilities at high risk of operational disruption due to safety lapses:\n\n"

    for index, row in high_risk_locations.iterrows():
        email_body += (
            f"Location: {row['CITY']}, {row['COUNTRY']}\n"
            f"- Safety Risk Score: {row['Safety_Risk_Score']:.2f}\n"
            f"- Repairs Per 1000 Units: {row['Repairs_Per_K_Units']:.2f}\n"
            f"- Average QA Pass Rate: {row['QA_Pass_Rate']:.2f}\n\n"
        )
    
    msg = MIMEText(email_body)
    msg['Subject'] = "High-Risk Safety Alert"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Safety alert email sent successfully.")
    except Exception as e:
        print(f"Failed to send safety email: {e}")