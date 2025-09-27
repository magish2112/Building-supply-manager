from flask import Flask
from flask_caching import Cache
import os

# Import configuration
from config.app_config import config

# Import database models
from models.database import db

# Import controllers
from controllers.request_controller import request_bp
from controllers.supplier_controller import supplier_bp
from controllers.site_controller import site_bp
from controllers.api_controller import api_bp

# Import utilities
from utils.notification_setup import setup_notifications, setup_logging

# Import demo data initializer
from init_demo_data import create_demo_data

def create_app(config_name='development'):
    """Application factory pattern"""

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    # Initialize caching
    cache = Cache(app)

    # Setup logging
    setup_logging(app)

    # Setup notifications
    setup_notifications(app)

    # Register blueprints
    app.register_blueprint(request_bp)
    app.register_blueprint(supplier_bp, url_prefix='/suppliers')
    app.register_blueprint(site_bp, url_prefix='/sites')
    app.register_blueprint(api_bp)

    # Add URL rules for main routes to work with blueprints
    with app.app_context():
        # Create database tables
        db.create_all()

        # Create demo data if tables are empty
        try:
            create_demo_data()
        except Exception as e:
            app.logger.warning(f"Could not create demo data: {e}")

        # Add main routes
        @app.route('/')
        def index():
            return request_bp.view_functions['request_bp.index']()

        @app.route('/requests')
        def requests_list():
            return request_bp.view_functions['request_bp.requests_list']()

        @app.route('/request/new', methods=['GET', 'POST'])
        def new_request():
            return request_bp.view_functions['request_bp.new_request']()

        @app.route('/request/<int:request_id>')
        def request_detail(request_id):
            return request_bp.view_functions['request_bp.request_detail'](request_id)

        @app.route('/request/<int:request_id>/edit', methods=['GET', 'POST'])
        def edit_request(request_id):
            return request_bp.view_functions['request_bp.edit_request'](request_id)

        @app.route('/request/<int:request_id>/update_status', methods=['POST'])
        def update_status(request_id):
            return request_bp.view_functions['request_bp.update_status'](request_id)

        @app.route('/suppliers')
        def suppliers_list():
            return supplier_bp.view_functions['supplier_bp.suppliers_list']()

        @app.route('/supplier/new', methods=['GET', 'POST'])
        def new_supplier():
            return supplier_bp.view_functions['supplier_bp.new_supplier']()

        @app.route('/supplier/<int:supplier_id>/edit', methods=['GET', 'POST'])
        def edit_supplier(supplier_id):
            return supplier_bp.view_functions['supplier_bp.edit_supplier'](supplier_id)

        @app.route('/supplier/<int:supplier_id>/delete', methods=['POST'])
        def delete_supplier(supplier_id):
            return supplier_bp.view_functions['supplier_bp.delete_supplier'](supplier_id)

        @app.route('/sites')
        def sites_list():
            return site_bp.view_functions['site_bp.sites_list']()

        @app.route('/site/new', methods=['GET', 'POST'])
        def new_site():
            return site_bp.view_functions['site_bp.new_site']()

        @app.route('/site/<int:site_id>/edit', methods=['GET', 'POST'])
        def edit_site(site_id):
            return site_bp.view_functions['site_bp.edit_site'](site_id)

        @app.route('/site/<int:site_id>/delete', methods=['POST'])
        def delete_site(site_id):
            return site_bp.view_functions['site_bp.site_delete'](site_id)

        @app.route('/api/stats')
        def api_stats():
            return request_bp.view_functions['request_bp.api_stats']()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

