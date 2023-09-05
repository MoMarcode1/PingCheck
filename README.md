
# IP Monitor and Notifier

## Description

This script continuously monitors a list of IP addresses to check their online status. If any IP address goes offline for more than 10 minutes, an email notification is sent to the configured email address. Every 10 hours, a summary email is also sent out, indicating the online status of all monitored IP addresses.

## Features

- Monitor multiple IP addresses simultaneously.
- Send email notifications when an IP address is offline for more than 10 minutes.
- Sends an online status summary of all IP addresses every 10 hours.
- Configuration through an external JSON file for ease of setup and modifications.
  
## Setup

### Prerequisites

- Python 3.x
- Required Python libraries: `smtplib`, `subprocess`, `time`, `json`

### Configuration

1. Edit the `config.json` file with the appropriate information:

```json
{
    "IP_TO_NAME": {
        "192.168.1.57": "Camera 1",
        "192.168.1.58": "Camera 2"
    },
    "EMAIL_SETTINGS": {
        "to_email": "recipient@example.com",
        "from_email": "your_email@example.com",
        "smtp_server": "smtp-mail.outlook.com",
        "smtp_port": 587,
        "smtp_user": "your_email@example.com",
        "smtp_pass": "your_password"
    }
}
```

- `IP_TO_NAME`: A dictionary mapping IP addresses to their respective names or identifiers.
- `EMAIL_SETTINGS`: Configuration for the SMTP email service used to send notifications.

2. Ensure that the system running the script allows outbound SMTP traffic on the configured port.

### Running

Execute the script either by double-clicking or through the command line:

```
python main.py
```

## Limitations

- The script uses simple ICMP pings to determine online status. Some devices might not respond to pings even if they are online.
- Continuously sending emails in quick succession, especially with the same content, can often trigger spam filters or rate limits on the email service.
