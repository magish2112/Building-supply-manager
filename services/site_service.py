from typing import List, Dict, Any
from ..models.database import db, ConstructionSite
from ..observers.base_observer import Subject, EventTypes
import logging

logger = logging.getLogger(__name__)

class SiteService(Subject):
    """Service for managing construction sites"""

    def __init__(self):
        super().__init__()
        self._cache = {}

    def create_site(self, data: Dict[str, Any]) -> ConstructionSite:
        """Create a new construction site"""
        try:
            # Validate data
            self._validate_site_data(data)

            site = ConstructionSite(
                name=data['name'],
                address=data.get('address'),
                manager=data.get('manager'),
                phone=data.get('phone')
            )

            db.session.add(site)
            db.session.commit()

            # Clear cache
            self._clear_cache()

            # Notify observers
            event_data = site.to_dict()
            self.notify(EventTypes.SITE_CREATED, event_data)

            logger.info(f"Created new site: {site.id}")
            return site

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create site: {e}")
            raise

    def update_site(self, site_id: int, data: Dict[str, Any]) -> ConstructionSite:
        """Update an existing site"""
        try:
            site = ConstructionSite.query.get_or_404(site_id)

            # Validate data
            self._validate_site_data(data, update=True)

            # Update fields
            for field in ['name', 'address', 'manager', 'phone']:
                if field in data:
                    setattr(site, field, data[field])

            db.session.commit()

            # Clear cache
            self._clear_cache()

            logger.info(f"Updated site: {site_id}")
            return site

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update site {site_id}: {e}")
            raise

    def get_site(self, site_id: int) -> ConstructionSite:
        """Get site by ID with caching"""
        cache_key = f"site_{site_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        site = ConstructionSite.query.get_or_404(site_id)
        self._cache[cache_key] = site
        return site

    def get_sites(self) -> List[ConstructionSite]:
        """Get all sites"""
        cache_key = "sites_all"
        if cache_key in self._cache:
            return self._cache[cache_key]

        sites = ConstructionSite.query.order_by(ConstructionSite.name).all()
        self._cache[cache_key] = sites
        return sites

    def delete_site(self, site_id: int) -> None:
        """Delete a site"""
        try:
            site = ConstructionSite.query.get_or_404(site_id)
            db.session.delete(site)
            db.session.commit()

            # Clear cache
            self._clear_cache()

            logger.info(f"Deleted site: {site_id}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete site {site_id}: {e}")
            raise

    def _validate_site_data(self, data: Dict[str, Any], update: bool = False) -> None:
        """Validate site data"""
        if not update and not data.get('name'):
            raise ValueError("Site name is required")

    def _clear_cache(self) -> None:
        """Clear all cached data"""
        self._cache.clear()

