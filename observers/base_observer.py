from abc import ABC, abstractmethod
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

class Observer(ABC):
    """Abstract base class for all observers"""

    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Called when an observed event occurs"""
        pass

class Subject:
    """Subject class that observers can subscribe to"""

    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        """Attach an observer to this subject"""
        if observer not in self._observers:
            self._observers.append(observer)
            logger.info(f"Observer {observer.__class__.__name__} attached")

    def detach(self, observer: Observer) -> None:
        """Detach an observer from this subject"""
        try:
            self._observers.remove(observer)
            logger.info(f"Observer {observer.__class__.__name__} detached")
        except ValueError:
            logger.warning(f"Observer {observer.__class__.__name__} not found")

    def notify(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notify all observers about an event"""
        logger.info(f"Notifying {len(self._observers)} observers about event: {event_type}")

        for observer in self._observers:
            try:
                observer.update(event_type, data)
            except Exception as e:
                logger.error(f"Error notifying observer {observer.__class__.__name__}: {e}")

class EventTypes:
    """Constants for event types"""
    REQUEST_CREATED = "request_created"
    REQUEST_STATUS_CHANGED = "request_status_changed"
    REQUEST_UPDATED = "request_updated"
    SUPPLIER_CREATED = "supplier_created"
    SITE_CREATED = "site_created"

