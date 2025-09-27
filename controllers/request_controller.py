from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from wtforms import Form, StringField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired
from datetime import date
from ..services.request_service import RequestService
from ..services.supplier_service import SupplierService
from ..services.site_service import SiteService
from ..models.database import SupplyRequest
import logging

logger = logging.getLogger(__name__)

# Create blueprint
request_bp = Blueprint('request_bp', __name__)

# Initialize services
request_service = RequestService()
supplier_service = SupplierService()
site_service = SiteService()

# Forms
class SupplyRequestForm(Form):
    title = StringField('Название заявки', validators=[DataRequired()])
    description = TextAreaField('Описание')
    material_name = StringField('Название материала')
    quantity = StringField('Количество')
    unit = StringField('Единица измерения')
    priority = SelectField('Приоритет', choices=[
        ('Низкий', 'Низкий'),
        ('Средний', 'Средний'),
        ('Высокий', 'Высокий'),
        ('Критический', 'Критический')
    ], default='Средний')
    status = SelectField('Статус', choices=[
        ('Новая', 'Новая'),
        ('В работе', 'В работе'),
        ('Ожидает поставки', 'Ожидает поставки'),
        ('Выполнена', 'Выполнена'),
        ('Отменена', 'Отменена')
    ], default='Новая')
    budget = StringField('Бюджет')
    supplier_id = SelectField('Поставщик', coerce=int)
    site_id = SelectField('Объект', coerce=int)
    deadline = DateField('Срок выполнения')
    notes = TextAreaField('Заметки')

@request_bp.route('/')
def index():
    """Main dashboard"""
    try:
        # Get recent requests
        requests = request_service.get_requests(limit=10)

        # Get statistics
        stats = request_service.get_request_stats()

        return render_template('index.html', requests=requests, stats=stats)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        flash('Ошибка загрузки дашборда', 'error')
        return render_template('index.html', requests=[], stats={})

@request_bp.route('/requests')
def requests_list():
    """List all requests with filtering"""
    try:
        status_filter = request.args.get('status', '')
        priority_filter = request.args.get('priority', '')

        requests = request_service.get_requests(
            status_filter=status_filter if status_filter else None,
            priority_filter=priority_filter if priority_filter else None
        )

        return render_template('requests.html', requests=requests, today=date.today())
    except Exception as e:
        logger.error(f"Error loading requests list: {e}")
        flash('Ошибка загрузки списка заявок', 'error')
        return render_template('requests.html', requests=[], today=date.today())

@request_bp.route('/request/new', methods=['GET', 'POST'])
def new_request():
    """Create new request"""
    form = SupplyRequestForm()
    form.supplier_id.choices = [(0, 'Не выбран')] + [(s.id, s.name) for s in supplier_service.get_suppliers()]
    form.site_id.choices = [(0, 'Не выбран')] + [(s.id, s.name) for s in site_service.get_sites()]

    if form.validate_on_submit():
        try:
            data = {
                'title': form.title.data,
                'description': form.description.data,
                'material_name': form.material_name.data,
                'quantity': form.quantity.data,
                'unit': form.unit.data,
                'priority': form.priority.data,
                'status': form.status.data,
                'budget': form.budget.data,
                'supplier_id': form.supplier_id.data if form.supplier_id.data != 0 else None,
                'site_id': form.site_id.data if form.site_id.data != 0 else None,
                'deadline': form.deadline.data,
                'notes': form.notes.data
            }

            new_request_obj = request_service.create_request(data)
            flash('Заявка создана успешно!', 'success')
            return redirect(url_for('request_bp.requests_list'))

        except ValueError as e:
            flash(f'Ошибка валидации: {str(e)}', 'error')
        except Exception as e:
            logger.error(f"Error creating request: {e}")
            flash('Ошибка создания заявки', 'error')

    return render_template('request_form.html', form=form, title='Новая заявка')

@request_bp.route('/request/<int:request_id>')
def request_detail(request_id):
    """View request details"""
    try:
        request_obj = request_service.get_request(request_id)
        return render_template('request_detail.html', request=request_obj, today=date.today())
    except Exception as e:
        logger.error(f"Error loading request {request_id}: {e}")
        flash('Заявка не найдена', 'error')
        return redirect(url_for('request_bp.requests_list'))

@request_bp.route('/request/<int:request_id>/edit', methods=['GET', 'POST'])
def edit_request(request_id):
    """Edit existing request"""
    try:
        request_obj = request_service.get_request(request_id)
        form = SupplyRequestForm(obj=request_obj)
        form.supplier_id.choices = [(0, 'Не выбран')] + [(s.id, s.name) for s in supplier_service.get_suppliers()]
        form.site_id.choices = [(0, 'Не выбран')] + [(s.id, s.name) for s in site_service.get_sites()]

        if form.validate_on_submit():
            try:
                data = {
                    'title': form.title.data,
                    'description': form.description.data,
                    'material_name': form.material_name.data,
                    'quantity': form.quantity.data,
                    'unit': form.unit.data,
                    'priority': form.priority.data,
                    'status': form.status.data,
                    'budget': form.budget.data,
                    'supplier_id': form.supplier_id.data if form.supplier_id.data != 0 else None,
                    'site_id': form.site_id.data if form.site_id.data != 0 else None,
                    'deadline': form.deadline.data,
                    'notes': form.notes.data
                }

                request_service.update_request(request_id, data)
                flash('Заявка обновлена успешно!', 'success')
                return redirect(url_for('request_bp.request_detail', request_id=request_id))

            except ValueError as e:
                flash(f'Ошибка валидации: {str(e)}', 'error')
            except Exception as e:
                logger.error(f"Error updating request {request_id}: {e}")
                flash('Ошибка обновления заявки', 'error')

        return render_template('request_form.html', form=form, title='Редактировать заявку')

    except Exception as e:
        logger.error(f"Error loading request {request_id} for editing: {e}")
        flash('Заявка не найдена', 'error')
        return redirect(url_for('request_bp.requests_list'))

@request_bp.route('/request/<int:request_id>/update_status', methods=['POST'])
def update_status(request_id):
    """Update request status"""
    try:
        new_status = request.form.get('status')
        comment = request.form.get('comment', '')

        if new_status and new_status in SupplyRequest.STATUS_CHOICES:
            request_service.update_request_status(request_id, new_status, comment)
            flash('Статус обновлен!', 'success')
        else:
            flash('Неверный статус', 'error')

    except Exception as e:
        logger.error(f"Error updating status for request {request_id}: {e}")
        flash('Ошибка обновления статуса', 'error')

    return redirect(url_for('request_bp.request_detail', request_id=request_id))

@request_bp.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    try:
        stats = request_service.get_request_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': 'Failed to get statistics'}), 500

