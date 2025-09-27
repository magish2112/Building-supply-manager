import os
import logging
from ..services.request_service import RequestService
from ..services.supplier_service import SupplierService
from ..services.site_service import SiteService
from ..observers.notification_observers import (
    EmailNotificationObserver,
    SlackNotificationObserver,
    LogNotificationObserver
)

logger = logging.getLogger(__name__)

def setup_notifications(app):
    """Setup notification observers for all services"""

    # Get configuration
    enable_notifications = app.config.get('ENABLE_NOTIFICATIONS', True)
    email_notifications = app.config.get('EMAIL_NOTIFICATIONS', False)
    slack_notifications = app.config.get('SLACK_NOTIFICATIONS', False)

    if not enable_notifications:
        logger.info("Notifications are disabled")
        return

    # Initialize services
    request_service = RequestService()
    supplier_service = SupplierService()
    site_service = SiteService()

    # Always add log observer
    log_observer = LogNotificationObserver()
    request_service.attach(log_observer)
    supplier_service.attach(log_observer)
    site_service.attach(log_observer)

    logger.info("Log notification observer attached to all services")

    # Setup email notifications if enabled
    if email_notifications:
        try:
            email_observer = EmailNotificationObserver(
                smtp_server=os.environ.get('SMTP_SERVER', 'smtp.gmail.com'),
                smtp_port=int(os.environ.get('SMTP_PORT', '587')),
                username=os.environ.get('SMTP_USERNAME', ''),
                password=os.environ.get('SMTP_PASSWORD', ''),
                from_email=os.environ.get('SMTP_FROM_EMAIL', '')
            )

            request_service.attach(email_observer)
            supplier_service.attach(email_observer)
            site_service.attach(email_observer)

            logger.info("Email notification observer attached to all services")

        except Exception as e:
            logger.error(f"Failed to setup email notifications: {e}")

    # Setup Slack notifications if enabled
    if slack_notifications:
        try:
            slack_webhook = os.environ.get('SLACK_WEBHOOK_URL', '')
            if slack_webhook:
                slack_observer = SlackNotificationObserver(slack_webhook)
                request_service.attach(slack_observer)
                logger.info("Slack notification observer attached to request service")
            else:
                logger.warning("Slack webhook URL not configured")

        except Exception as e:
            logger.error(f"Failed to setup Slack notifications: {e}")

def setup_logging(app):
    """Setup application logging"""

    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/supply_tracker.log'),
            logging.StreamHandler()
        ]
    )

    # Set Flask logging level
    if app.debug:
        logging.getLogger('werkzeug').setLevel(logging.DEBUG)
    else:
        logging.getLogger('werkzeug').setLevel(logging.WARNING)

    logger.info("Logging configured successfully")

