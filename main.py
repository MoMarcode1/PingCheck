import smtplib
from email.message import EmailMessage
import subprocess
import time
import json


def is_ip_pingable(ip_address):
    """Check if the IP is pingable."""
    response = subprocess.run(['ping', '-n', '1', ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_text = response.stdout.decode('utf-8', errors='replace')

    # Check for phrases that indicate failure
    failure_phrases = ["Zielhost nicht erreichbar", "Zeitüberschreitung der Anforderung"]
    if any(phrase in stdout_text for phrase in failure_phrases):
        print(f"{ip_address} is not reachable.")
        return False
    else:
        print(f"{ip_address} is reachable.")
        return response.returncode == 0


def send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_pass):
    """Send an email using SMTP."""
    print(f"Sending email with subject: {subject}")
    email = EmailMessage()
    email["From"] = from_email
    email["To"] = to_email
    email["Subject"] = subject
    email.set_content(body)

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_user, smtp_pass)
        smtp.sendmail(from_email, to_email, email.as_string())


# Load configurations from the JSON file
with open('config.json', 'r') as file:
    config = json.load(file)

IP_TO_NAME = config["IP_TO_NAME"]
EMAIL_SETTINGS = config["EMAIL_SETTINGS"]


def main():
    print("Program started.")

    # Dictionary to track downtime start times and IP status
    downtime_starts = {ip: None for ip in IP_TO_NAME.keys()}
    ip_status = {ip: "Not Checked" for ip in IP_TO_NAME.keys()}
    last_summary_time = time.time()  # Initialize to current time

    # Send initial online notification
    for ip in IP_TO_NAME.keys():
        device_name = IP_TO_NAME.get(ip, ip)
        if is_ip_pingable(ip):
            ip_status[ip] = "Online"
            send_email(
                f"{device_name} (IP Address {ip}) Online",
                f"{device_name} with IP address {ip} is online.",
                **EMAIL_SETTINGS
            )
        else:
            ip_status[ip] = "Offline"

    while True:
        print("Starting new check cycle.")
        for ip in IP_TO_NAME.keys():
            device_name = IP_TO_NAME.get(ip, ip)
            if not is_ip_pingable(ip):
                ip_status[ip] = "Offline"
                if downtime_starts[ip] is None:
                    downtime_starts[ip] = time.time()
                elif time.time() - downtime_starts[ip] >= 600:  # 600 seconds = 10 minutes
                    send_email(
                        f"{device_name} (IP Address {ip}) Down",
                        f"{device_name} with IP address {ip} has been down for 10 minutes.",
                        **EMAIL_SETTINGS
                    )
                    downtime_starts[ip] = None  # reset the timer after sending the email
            else:
                ip_status[ip] = "Online"
                downtime_starts[ip] = None  # reset the timer if the IP is back up

        # Check if it's time to send the summary email
        if time.time() - last_summary_time >= 36000:  # Every 10 hours (36000 seconds)
            status_message = "\n".join(
                [f"{IP_TO_NAME.get(ip, ip)} ({ip}): {status}" for ip, status in ip_status.items()])
            send_email(
                "IP Address Status Summary",
                status_message,
                **EMAIL_SETTINGS
            )
            last_summary_time = time.time()  # Reset the timer

        print("Check cycle completed. Sleeping for 30 seconds.")
        time.sleep(30)  # Check every 30 seconds


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
