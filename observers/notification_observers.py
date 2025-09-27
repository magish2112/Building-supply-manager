import logging
from typing import Dict, Any
from .base_observer import Observer
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json

logger = logging.getLogger(__name__)

class EmailNotificationObserver(Observer):
    """Observer that sends email notifications"""

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, from_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email

    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Send email notification based on event type"""
        try:
            if event_type == "request_status_changed":
                self._send_status_change_email(data)
            elif event_type == "request_created":
                self._send_request_created_email(data)
            elif event_type == "supplier_created":
                self._send_supplier_created_email(data)
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")

    def _send_status_change_email(self, data: Dict[str, Any]) -> None:
        """Send email about status change"""
        subject = f"Заявка #{data['request_id']}: статус изменен"
        body = f"""
        Заявка #{data['request_id']} "{data['title']}" изменила статус:
        {data['old_status']} → {data['new_status']}

        Объект: {data.get('site_name', 'Не указан')}
        Поставщик: {data.get('supplier_name', 'Не указан')}

        Комментарий: {data.get('comment', 'Без комментария')}

        Ссылка: {data.get('request_url', '#')}
        """

        self._send_email(subject, body)

    def _send_request_created_email(self, data: Dict[str, Any]) -> None:
        """Send email about new request"""
        subject = f"Новая заявка #{data['request_id']}: {data['title']}"
        body = f"""
        Создана новая заявка #{data['request_id']}:
        Название: {data['title']}
        Приоритет: {data['priority']}
        Материал: {data.get('material_name', 'Не указан')}

        Объект: {data.get('site_name', 'Не указан')}
        Поставщик: {data.get('supplier_name', 'Не указан')}

        Ссылка: {data.get('request_url', '#')}
        """

        self._send_email(subject, body)

    def _send_supplier_created_email(self, data: Dict[str, Any]) -> None:
        """Send email about new supplier"""
        subject = f"Новый поставщик: {data['name']}"
        body = f"""
        Добавлен новый поставщик:
        Название: {data['name']}
        Контактное лицо: {data.get('contact_person', 'Не указано')}
        Телефон: {data.get('phone', 'Не указан')}
        Email: {data.get('email', 'Не указан')}
        """

        self._send_email(subject, body)

    def _send_email(self, subject: str, body: str) -> None:
        """Send email using SMTP"""
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = self.from_email  # In real app, this would be configurable recipients
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.from_email, self.from_email, text)
            server.quit()
            logger.info(f"Email sent: {subject}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

class SlackNotificationObserver(Observer):
    """Observer that sends Slack notifications"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Send Slack notification based on event type"""
        try:
            if event_type == "request_status_changed":
                self._send_status_change_slack(data)
            elif event_type == "request_created":
                self._send_request_created_slack(data)
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")

    def _send_status_change_slack(self, data: Dict[str, Any]) -> None:
        """Send Slack message about status change"""
        message = {
            "text": f"🔄 Заявка #{data['request_id']}: {data['old_status']} → {data['new_status']}",
            "attachments": [
                {
                    "color": self._get_status_color(data['new_status']),
                    "fields": [
                        {"title": "Заявка", "value": data['title'], "short": True},
                        {"title": "Приоритет", "value": data['priority'], "short": True},
                        {"title": "Объект", "value": data.get('site_name', 'Не указан'), "short": True},
                        {"title": "Поставщик", "value": data.get('supplier_name', 'Не указан'), "short": True},
                        {"title": "Комментарий", "value": data.get('comment', 'Без комментария'), "short": False}
                    ]
                }
            ]
        }
        self._send_slack_message(message)

    def _send_request_created_slack(self, data: Dict[str, Any]) -> None:
        """Send Slack message about new request"""
        message = {
            "text": f"📋 Новая заявка #{data['request_id']}",
            "attachments": [
                {
                    "color": "good",
                    "fields": [
                        {"title": "Название", "value": data['title'], "short": True},
                        {"title": "Приоритет", "value": data['priority'], "short": True},
                        {"title": "Материал", "value": data.get('material_name', 'Не указан'), "short": True},
                        {"title": "Объект", "value": data.get('site_name', 'Не указан'), "short": True},
                        {"title": "Поставщик", "value": data.get('supplier_name', 'Не указан'), "short": True}
                    ]
                }
            ]
        }
        self._send_slack_message(message)

    def _send_slack_message(self, message: Dict[str, Any]) -> None:
        """Send message to Slack webhook"""
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(message),
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                logger.info("Slack notification sent successfully")
            else:
                logger.error(f"Failed to send Slack notification: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")

    def _get_status_color(self, status: str) -> str:
        """Get color for status"""
        colors = {
            'Новая': 'warning',
            'В работе': 'good',
            'Ожидает поставки': 'danger',
            'Выполнена': 'good',
            'Отменена': 'danger'
        }
        return colors.get(status, 'warning')

class LogNotificationObserver(Observer):
    """Observer that logs events to file"""

    def __init__(self, log_file: str = "supply_notifications.log"):
        self.logger = logging.getLogger("supply_notifications")
        self.logger.setLevel(logging.INFO)

        # Create file handler
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Add handler to logger
        self.logger.addHandler(handler)

    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log the event"""
        if event_type == "request_status_changed":
            message = f"Request #{data['request_id']} status changed: {data['old_status']} -> {data['new_status']}"
            if data.get('comment'):
                message += f" (Comment: {data['comment']})"
        elif event_type == "request_created":
            message = f"New request created: #{data['request_id']} - {data['title']}"
        elif event_type == "supplier_created":
            message = f"New supplier created: {data['name']}"
        elif event_type == "site_created":
            message = f"New site created: {data['name']}"
        else:
            message = f"Event {event_type}: {data}"

        self.logger.info(message)

