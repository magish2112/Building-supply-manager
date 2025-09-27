import unittest
from unittest.mock import patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app_new import create_app
from models.database import db
from services.request_service import RequestService
from services.supplier_service import SupplierService
from services.site_service import SiteService

class TestServices(unittest.TestCase):
    """Test cases for service layer"""

    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Initialize services
        self.request_service = RequestService()
        self.supplier_service = SupplierService()
        self.site_service = SiteService()

    def tearDown(self):
        """Tear down test fixtures"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_supplier(self):
        """Test supplier creation"""
        data = {
            'name': 'Test Supplier',
            'contact_person': 'John Doe',
            'phone': '+1234567890',
            'email': 'john@example.com',
            'address': 'Test Address'
        }

        supplier = self.supplier_service.create_supplier(data)

        self.assertEqual(supplier.name, 'Test Supplier')
        self.assertEqual(supplier.contact_person, 'John Doe')
        self.assertEqual(supplier.email, 'john@example.com')

    def test_create_site(self):
        """Test site creation"""
        data = {
            'name': 'Test Construction Site',
            'address': 'Test Site Address',
            'manager': 'Jane Smith',
            'phone': '+0987654321'
        }

        site = self.site_service.create_site(data)

        self.assertEqual(site.name, 'Test Construction Site')
        self.assertEqual(site.manager, 'Jane Smith')

    def test_create_request(self):
        """Test request creation"""
        # First create supplier and site
        supplier_data = {'name': 'Test Supplier'}
        site_data = {'name': 'Test Site'}

        supplier = self.supplier_service.create_supplier(supplier_data)
        site = self.site_service.create_site(site_data)

        # Create request
        request_data = {
            'title': 'Test Request',
            'description': 'Test description',
            'material_name': 'Test Material',
            'quantity': '100',
            'unit': 'kg',
            'priority': 'Высокий',
            'supplier_id': supplier.id,
            'site_id': site.id
        }

        request_obj = self.request_service.create_request(request_data)

        self.assertEqual(request_obj.title, 'Test Request')
        self.assertEqual(request_obj.priority, 'Высокий')
        self.assertEqual(request_obj.supplier_id, supplier.id)
        self.assertEqual(request_obj.site_id, site.id)

    def test_request_validation(self):
        """Test request validation"""
        # Test missing title
        with self.assertRaises(ValueError):
            self.request_service.create_request({})

        # Test invalid priority
        with self.assertRaises(ValueError):
            self.request_service.create_request({
                'title': 'Test',
                'priority': 'Invalid Priority'
            })

    def test_supplier_validation(self):
        """Test supplier validation"""
        # Test missing name
        with self.assertRaises(ValueError):
            self.supplier_service.create_supplier({})

        # Test invalid email
        with self.assertRaises(ValueError):
            self.supplier_service.create_supplier({
                'name': 'Test',
                'email': 'invalid-email'
            })

    def test_update_request_status(self):
        """Test status update"""
        # Create a request first
        supplier = self.supplier_service.create_supplier({'name': 'Test Supplier'})
        site = self.site_service.create_site({'name': 'Test Site'})

        request_data = {
            'title': 'Test Request',
            'supplier_id': supplier.id,
            'site_id': site.id
        }

        request_obj = self.request_service.create_request(request_data)
        original_status = request_obj.status

        # Update status
        updated_request = self.request_service.update_request_status(
            request_obj.id, 'В работе', 'Status updated for testing'
        )

        self.assertNotEqual(updated_request.status, original_status)
        self.assertEqual(updated_request.status, 'В работе')

if __name__ == '__main__':
    unittest.main()

