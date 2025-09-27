from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from wtforms import Form, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Optional
from ..services.supplier_service import SupplierService
from ..models.database import Supplier
import logging

logger = logging.getLogger(__name__)

# Create blueprint
supplier_bp = Blueprint('supplier_bp', __name__)

# Initialize service
supplier_service = SupplierService()

# Forms
class SupplierForm(Form):
    name = StringField('Название компании', validators=[DataRequired()])
    contact_person = StringField('Контактное лицо')
    phone = StringField('Телефон')
    email = StringField('Email', validators=[Optional(), Email()])
    address = TextAreaField('Адрес')
    submit = SubmitField('Сохранить')

@supplier_bp.route('/')
def suppliers():
    """List all suppliers"""
    try:
        suppliers = supplier_service.get_all_suppliers()
        return render_template('suppliers.html', suppliers=suppliers)
    except Exception as e:
        logger.error(f"Error getting suppliers: {str(e)}")
        flash('Ошибка при загрузке поставщиков', 'error')
        return render_template('suppliers.html', suppliers=[])

@supplier_bp.route('/new', methods=['GET', 'POST'])
def new_supplier():
    """Create new supplier"""
    form = SupplierForm(request.form)

    if request.method == 'POST' and form.validate():
        try:
            data = {
                'name': form.name.data,
                'contact_person': form.contact_person.data,
                'phone': form.phone.data,
                'email': form.email.data,
                'address': form.address.data
            }

            supplier_service.create_supplier(data)
            flash('Поставщик успешно создан', 'success')
            return redirect(url_for('supplier_bp.suppliers'))

        except Exception as e:
            logger.error(f"Error creating supplier: {str(e)}")
            flash('Ошибка при создании поставщика', 'error')

    return render_template('supplier_form.html', form=form, title='Новый поставщик')

@supplier_bp.route('/<int:supplier_id>/edit', methods=['GET', 'POST'])
def edit_supplier(supplier_id):
    """Edit supplier"""
    supplier = supplier_service.get_supplier_by_id(supplier_id)
    if not supplier:
        flash('Поставщик не найден', 'error')
        return redirect(url_for('supplier_bp.suppliers'))

    form = SupplierForm(request.form, obj=supplier)

    if request.method == 'POST' and form.validate():
        try:
            data = {
                'name': form.name.data,
                'contact_person': form.contact_person.data,
                'phone': form.phone.data,
                'email': form.email.data,
                'address': form.address.data
            }

            supplier_service.update_supplier(supplier_id, data)
            flash('Поставщик успешно обновлен', 'success')
            return redirect(url_for('supplier_bp.suppliers'))

        except Exception as e:
            logger.error(f"Error updating supplier {supplier_id}: {str(e)}")
            flash('Ошибка при обновлении поставщика', 'error')

    return render_template('supplier_form.html', form=form, title='Редактировать поставщика')

@supplier_bp.route('/<int:supplier_id>/delete', methods=['POST'])
def delete_supplier(supplier_id):
    """Delete supplier"""
    try:
        supplier_service.delete_supplier(supplier_id)
        flash('Поставщик успешно удален', 'success')
    except Exception as e:
        logger.error(f"Error deleting supplier {supplier_id}: {str(e)}")
        flash('Ошибка при удалении поставщика', 'error')

    return redirect(url_for('supplier_bp.suppliers'))
