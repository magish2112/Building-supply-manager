from typing import List, Dict, Any
from ..models.database import db, Supplier
from ..observers.base_observer import Subject, EventTypes
import logging

logger = logging.getLogger(__name__)

class SupplierService(Subject):
    """Service for managing suppliers"""

    def __init__(self):
        super().__init__()
        self._cache = {}

    def create_supplier(self, data: Dict[str, Any]) -> Supplier:
        """Create a new supplier"""
        try:
            # Validate data
            self._validate_supplier_data(data)

            supplier = Supplier(
                name=data['name'],
                contact_person=data.get('contact_person'),
                phone=data.get('phone'),
                email=data.get('email'),
                address=data.get('address')
            )

            db.session.add(supplier)
            db.session.commit()

            # Clear cache
            self._clear_cache()

            # Notify observers
            event_data = supplier.to_dict()
            self.notify(EventTypes.SUPPLIER_CREATED, event_data)

            logger.info(f"Created new supplier: {supplier.id}")
            return supplier

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create supplier: {e}")
            raise

    def update_supplier(self, supplier_id: int, data: Dict[str, Any]) -> Supplier:
        """Update an existing supplier"""
        try:
            supplier = Supplier.query.get_or_404(supplier_id)

            # Validate data
            self._validate_supplier_data(data, update=True)

            # Update fields
            for field in ['name', 'contact_person', 'phone', 'email', 'address']:
                if field in data:
                    setattr(supplier, field, data[field])

            db.session.commit()

            # Clear cache
            self._clear_cache()

            logger.info(f"Updated supplier: {supplier_id}")
            return supplier

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update supplier {supplier_id}: {e}")
            raise

    def get_supplier(self, supplier_id: int) -> Supplier:
        """Get supplier by ID with caching"""
        cache_key = f"supplier_{supplier_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        supplier = Supplier.query.get_or_404(supplier_id)
        self._cache[cache_key] = supplier
        return supplier

    def get_suppliers(self) -> List[Supplier]:
        """Get all suppliers"""
        cache_key = "suppliers_all"
        if cache_key in self._cache:
            return self._cache[cache_key]

        suppliers = Supplier.query.order_by(Supplier.name).all()
        self._cache[cache_key] = suppliers
        return suppliers

    def delete_supplier(self, supplier_id: int) -> None:
        """Delete a supplier"""
        try:
            supplier = Supplier.query.get_or_404(supplier_id)
            db.session.delete(supplier)
            db.session.commit()

            # Clear cache
            self._clear_cache()

            logger.info(f"Deleted supplier: {supplier_id}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete supplier {supplier_id}: {e}")
            raise

    def _validate_supplier_data(self, data: Dict[str, Any], update: bool = False) -> None:
        """Validate supplier data"""
        if not update and not data.get('name'):
            raise ValueError("Supplier name is required")

        # Validate email format if provided
        if data.get('email'):
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                raise ValueError("Invalid email format")

    def _clear_cache(self) -> None:
        """Clear all cached data"""
        self._cache.clear()
