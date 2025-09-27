from flask import Blueprint, request, jsonify, current_app
from ..services.request_service import RequestService
from ..services.supplier_service import SupplierService
from ..services.site_service import SiteService
from ..models.database import SupplyRequest, Supplier, ConstructionSite
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

# Create API blueprint
api_bp = Blueprint('api_bp', __name__, url_prefix='/api/v1')

# Initialize services
request_service = RequestService()
supplier_service = SupplierService()
site_service = SiteService()


# ================================
# REQUESTS API
# ================================

@api_bp.route('/requests', methods=['GET'])
def get_requests():
    """Get all supply requests with filtering and pagination"""
    try:
        # Query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        status = request.args.get('status')
        priority = request.args.get('priority')
        supplier_id = request.args.get('supplier_id')
        site_id = request.args.get('site_id')
        search = request.args.get('search')

        # Build query
        query = SupplyRequest.query

        if status:
            query = query.filter(SupplyRequest.status == status)
        if priority:
            query = query.filter(SupplyRequest.priority == priority)
        if supplier_id:
            query = query.filter(SupplyRequest.supplier_id == int(supplier_id))
        if site_id:
            query = query.filter(SupplyRequest.site_id == int(site_id))
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (SupplyRequest.title.ilike(search_term)) |
                (SupplyRequest.description.ilike(search_term)) |
                (SupplyRequest.material_name.ilike(search_term))
            )

        # Pagination
        total = query.count()
        requests = query.offset((page - 1) * per_page).limit(per_page).all()

        return jsonify({
            'success': True,
            'data': {
                'requests': [request_to_dict(req) for req in requests],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
        })

    except Exception as e:
        logger.error(f"Error getting requests: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/requests/<int:request_id>', methods=['GET'])
def get_request(request_id):
    """Get a specific request by ID"""
    try:
        request_obj = SupplyRequest.query.get_or_404(request_id)
        return jsonify({
            'success': True,
            'data': request_to_dict(request_obj, detailed=True)
        })

    except Exception as e:
        logger.error(f"Error getting request {request_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/requests', methods=['POST'])
def create_request():
    """Create a new supply request"""
    try:
        data = request.get_json()

        if not data or not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400

        # Create request using service
        new_request = request_service.create_request(data)

        return jsonify({
            'success': True,
            'data': request_to_dict(new_request),
            'message': 'Request created successfully'
        }), 201

    except Exception as e:
        logger.error(f"Error creating request: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/requests/<int:request_id>', methods=['PUT'])
def update_request(request_id):
    """Update a supply request"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update request using service
        updated_request = request_service.update_request(request_id, data)

        return jsonify({
            'success': True,
            'data': request_to_dict(updated_request),
            'message': 'Request updated successfully'
        })

    except Exception as e:
        logger.error(f"Error updating request {request_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/requests/<int:request_id>', methods=['DELETE'])
def delete_request(request_id):
    """Delete a supply request"""
    try:
        request_service.delete_request(request_id)
        return jsonify({
            'success': True,
            'message': 'Request deleted successfully'
        })

    except Exception as e:
        logger.error(f"Error deleting request {request_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/requests/<int:request_id>/status', methods=['PUT'])
def update_request_status(request_id):
    """Update request status"""
    try:
        data = request.get_json()
        if not data or not data.get('status'):
            return jsonify({'error': 'Status is required'}), 400

        new_status = data['status']
        comment = data.get('comment', '')

        # Update status using service
        updated_request = request_service.update_status(request_id, new_status, comment)

        return jsonify({
            'success': True,
            'data': request_to_dict(updated_request),
            'message': f'Status updated to {new_status}'
        })

    except Exception as e:
        logger.error(f"Error updating status for request {request_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ================================
# SUPPLIERS API
# ================================

@api_bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    """Get all suppliers"""
    try:
        suppliers = Supplier.query.all()
        return jsonify({
            'success': True,
            'data': [supplier_to_dict(supplier) for supplier in suppliers]
        })

    except Exception as e:
        logger.error(f"Error getting suppliers: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/suppliers/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    """Get a specific supplier"""
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        return jsonify({
            'success': True,
            'data': supplier_to_dict(supplier, detailed=True)
        })

    except Exception as e:
        logger.error(f"Error getting supplier {supplier_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/suppliers', methods=['POST'])
def create_supplier():
    """Create a new supplier"""
    try:
        data = request.get_json()

        if not data or not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400

        # Create supplier using service
        new_supplier = supplier_service.create_supplier(data)

        return jsonify({
            'success': True,
            'data': supplier_to_dict(new_supplier),
            'message': 'Supplier created successfully'
        }), 201

    except Exception as e:
        logger.error(f"Error creating supplier: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ================================
# SITES API
# ================================

@api_bp.route('/sites', methods=['GET'])
def get_sites():
    """Get all construction sites"""
    try:
        sites = ConstructionSite.query.all()
        return jsonify({
            'success': True,
            'data': [site_to_dict(site) for site in sites]
        })

    except Exception as e:
        logger.error(f"Error getting sites: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sites/<int:site_id>', methods=['GET'])
def get_site(site_id):
    """Get a specific construction site"""
    try:
        site = ConstructionSite.query.get_or_404(site_id)
        return jsonify({
            'success': True,
            'data': site_to_dict(site, detailed=True)
        })

    except Exception as e:
        logger.error(f"Error getting site {site_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ================================
# STATISTICS API
# ================================

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get application statistics"""
    try:
        # Request statistics
        total_requests = SupplyRequest.query.count()
        status_stats = {}
        for status in ['Новая', 'В работе', 'Ожидает поставки', 'Выполнена', 'Отменена']:
            status_stats[status] = SupplyRequest.query.filter_by(status=status).count()

        priority_stats = {}
        for priority in ['Низкий', 'Средний', 'Высокий', 'Критический']:
            priority_stats[priority] = SupplyRequest.query.filter_by(priority=priority).count()

        # Supplier and site counts
        total_suppliers = Supplier.query.count()
        total_sites = ConstructionSite.query.count()

        # Recent activity (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_requests = SupplyRequest.query.filter(SupplyRequest.created_at >= week_ago).count()

        return jsonify({
            'success': True,
            'data': {
                'requests': {
                    'total': total_requests,
                    'by_status': status_stats,
                    'by_priority': priority_stats,
                    'recent': recent_requests
                },
                'suppliers': {
                    'total': total_suppliers
                },
                'sites': {
                    'total': total_sites
                },
                'timestamp': datetime.utcnow().isoformat()
            }
        })

    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ================================
# HEALTH CHECK
# ================================

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Application health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'database': 'connected' if check_db_connection() else 'disconnected'
    })


# ================================
# HELPER FUNCTIONS
# ================================

def request_to_dict(req, detailed=False):
    """Convert SupplyRequest to dictionary"""
    data = {
        'id': req.id,
        'title': req.title,
        'description': req.description,
        'material_name': req.material_name,
        'quantity': req.quantity,
        'unit': req.unit,
        'priority': req.priority,
        'status': req.status,
        'budget': req.budget,
        'supplier_id': req.supplier_id,
        'site_id': req.site_id,
        'created_at': req.created_at.isoformat() if req.created_at else None,
        'updated_at': req.updated_at.isoformat() if req.updated_at else None,
        'deadline': req.deadline.isoformat() if req.deadline else None,
        'notes': req.notes
    }

    if detailed:
        data['supplier'] = supplier_to_dict(req.supplier) if req.supplier else None
        data['site'] = site_to_dict(req.site) if req.site else None

    return data

def supplier_to_dict(sup, detailed=False):
    """Convert Supplier to dictionary"""
    data = {
        'id': sup.id,
        'name': sup.name,
        'contact_person': sup.contact_person,
        'phone': sup.phone,
        'email': sup.email,
        'address': sup.address,
        'created_at': sup.created_at.isoformat() if sup.created_at else None
    }

    if detailed:
        # Add request count
        data['request_count'] = len(sup.requests)

    return data

def site_to_dict(site, detailed=False):
    """Convert ConstructionSite to dictionary"""
    data = {
        'id': site.id,
        'name': site.name,
        'address': site.address,
        'manager': site.manager,
        'phone': site.phone,
        'created_at': site.created_at.isoformat() if site.created_at else None
    }

    if detailed:
        # Add request count
        data['request_count'] = len(site.requests)

    return data

def check_db_connection():
    """Check database connection"""
    try:
        db.session.execute(db.text('SELECT 1'))
        return True
    except Exception:
        return False
