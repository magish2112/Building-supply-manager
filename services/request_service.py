from typing import List, Optional, Dict, Any
from datetime import datetime
from flask import url_for
from ..models.database import db, SupplyRequest, Supplier, ConstructionSite, RequestUpdate
from ..observers.base_observer import Subject, EventTypes
import logging

logger = logging.getLogger(__name__)

class RequestService(Subject):
    """Service for managing supply requests with observer pattern"""

    def __init__(self):
        super().__init__()
        self._cache = {}  # Simple in-memory cache

    def create_request(self, data: Dict[str, Any]) -> SupplyRequest:
        """Create a new supply request"""
        try:
            # Validate data
            self._validate_request_data(data)

            # Create request
            request = SupplyRequest(
                title=data['title'],
                description=data.get('description'),
                material_name=data.get('material_name'),
                quantity=data.get('quantity'),
                unit=data.get('unit'),
                priority=data.get('priority', 'Средний'),
                status='Новая',
                budget=float(data['budget']) if data.get('budget') else None,
                supplier_id=data.get('supplier_id'),
                site_id=data.get('site_id'),
                deadline=data.get('deadline'),
                notes=data.get('notes')
            )

            db.session.add(request)
            db.session.commit()

            # Clear cache
            self._clear_cache()

            # Notify observers
            event_data = self._prepare_request_event_data(request)
            self.notify(EventTypes.REQUEST_CREATED, event_data)

            logger.info(f"Created new request: {request.id}")
            return request

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create request: {e}")
            raise

    def update_request(self, request_id: int, data: Dict[str, Any]) -> SupplyRequest:
        """Update an existing request"""
        try:
            request = SupplyRequest.query.get_or_404(request_id)

            # Validate data
            self._validate_request_data(data, update=True)

            # Update fields
            for field in ['title', 'description', 'material_name', 'quantity', 'unit',
                         'priority', 'budget', 'supplier_id', 'site_id', 'deadline', 'notes']:
                if field in data:
                    if field == 'budget' and data[field] is not None:
                        setattr(request, field, float(data[field]))
                    else:
                        setattr(request, field, data[field])

            request.updated_at = datetime.utcnow()
            db.session.commit()

            # Clear cache
            self._clear_cache()

            # Notify observers
            event_data = self._prepare_request_event_data(request)
            self.notify(EventTypes.REQUEST_UPDATED, event_data)

            logger.info(f"Updated request: {request_id}")
            return request

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update request {request_id}: {e}")
            raise

    def update_request_status(self, request_id: int, new_status: str, comment: Optional[str] = None) -> SupplyRequest:
        """Update request status with history tracking"""
        try:
            request = SupplyRequest.query.get_or_404(request_id)

            # Update status
            old_status = request.status
            request.update_status(new_status, comment)
            db.session.commit()

            # Clear cache
            self._clear_cache()

            # Notify observers
            event_data = self._prepare_request_event_data(request)
            event_data.update({
                'old_status': old_status,
                'comment': comment
            })
            self.notify(EventTypes.REQUEST_STATUS_CHANGED, event_data)

            logger.info(f"Updated request {request_id} status: {old_status} -> {new_status}")
            return request

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update request {request_id} status: {e}")
            raise

    def get_request(self, request_id: int) -> SupplyRequest:
        """Get request by ID with caching"""
        cache_key = f"request_{request_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        request = SupplyRequest.query.get_or_404(request_id)
        self._cache[cache_key] = request
        return request

    def get_requests(self, status_filter: Optional[str] = None,
                    priority_filter: Optional[str] = None,
                    limit: Optional[int] = None) -> List[SupplyRequest]:
        """Get requests with optional filtering"""
        query = SupplyRequest.query

        if status_filter:
            query = query.filter_by(status=status_filter)
        if priority_filter:
            query = query.filter_by(priority=priority_filter)

        query = query.order_by(SupplyRequest.created_at.desc())

        if limit:
            query = query.limit(limit)

        return query.all()

    def get_request_stats(self) -> Dict[str, int]:
        """Get request statistics"""
        cache_key = "request_stats"
        if cache_key in self._cache:
            return self._cache[cache_key]

        stats = {
            'total': SupplyRequest.query.count(),
            'new': SupplyRequest.query.filter_by(status='Новая').count(),
            'in_progress': SupplyRequest.query.filter_by(status='В работе').count(),
            'waiting': SupplyRequest.query.filter_by(status='Ожидает поставки').count(),
            'completed': SupplyRequest.query.filter_by(status='Выполнена').count(),
            'cancelled': SupplyRequest.query.filter_by(status='Отменена').count()
        }

        self._cache[cache_key] = stats
        return stats

    def delete_request(self, request_id: int) -> None:
        """Delete a request"""
        try:
            request = SupplyRequest.query.get_or_404(request_id)
            db.session.delete(request)
            db.session.commit()

            # Clear cache
            self._clear_cache()

            logger.info(f"Deleted request: {request_id}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete request {request_id}: {e}")
            raise

    def _validate_request_data(self, data: Dict[str, Any], update: bool = False) -> None:
        """Validate request data"""
        if not update and not data.get('title'):
            raise ValueError("Title is required")

        if data.get('priority') and data['priority'] not in SupplyRequest.PRIORITY_CHOICES:
            raise ValueError(f"Invalid priority: {data['priority']}")

        if data.get('status') and data['status'] not in SupplyRequest.STATUS_CHOICES:
            raise ValueError(f"Invalid status: {data['status']}")

        # Validate supplier and site exist if provided
        if data.get('supplier_id'):
            supplier = Supplier.query.get(data['supplier_id'])
            if not supplier:
                raise ValueError(f"Supplier with ID {data['supplier_id']} not found")

        if data.get('site_id'):
            site = ConstructionSite.query.get(data['site_id'])
            if not site:
                raise ValueError(f"Site with ID {data['site_id']} not found")

    def _prepare_request_event_data(self, request: SupplyRequest) -> Dict[str, Any]:
        """Prepare event data for observers"""
        return {
            'request_id': request.id,
            'title': request.title,
            'priority': request.priority,
            'status': request.status,
            'material_name': request.material_name,
            'site_name': request.site.name if request.site else None,
            'supplier_name': request.supplier.name if request.supplier else None,
            'request_url': url_for('request_detail', request_id=request.id, _external=True)
        }

    def _clear_cache(self) -> None:
        """Clear all cached data"""
        self._cache.clear()

