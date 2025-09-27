from flask import Blueprint, render_template, request, redirect, url_for, flash
from wtforms import Form, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from ..services.site_service import SiteService
import logging

logger = logging.getLogger(__name__)

# Create blueprint
site_bp = Blueprint('site_bp', __name__)

# Initialize service
site_service = SiteService()

# Forms
class SiteForm(Form):
    name = StringField('Название объекта', validators=[DataRequired()])
    address = TextAreaField('Адрес')
    manager = StringField('Менеджер')
    phone = StringField('Телефон')

@site_bp.route('/sites')
def sites_list():
    """List all sites"""
    try:
        sites = site_service.get_sites()
        return render_template('sites.html', sites=sites)
    except Exception as e:
        logger.error(f"Error loading sites list: {e}")
        flash('Ошибка загрузки списка объектов', 'error')
        return render_template('sites.html', sites=[])

@site_bp.route('/site/new', methods=['GET', 'POST'])
def new_site():
    """Create new site"""
    form = SiteForm()

    if form.validate_on_submit():
        try:
            data = {
                'name': form.name.data,
                'address': form.address.data,
                'manager': form.manager.data,
                'phone': form.phone.data
            }

            site_service.create_site(data)
            flash('Объект добавлен успешно!', 'success')
            return redirect(url_for('site_bp.sites_list'))

        except ValueError as e:
            flash(f'Ошибка валидации: {str(e)}', 'error')
        except Exception as e:
            logger.error(f"Error creating site: {e}")
            flash('Ошибка создания объекта', 'error')

    return render_template('site_form.html', form=form, title='Новый объект')

@site_bp.route('/site/<int:site_id>/edit', methods=['GET', 'POST'])
def edit_site(site_id):
    """Edit existing site"""
    try:
        site = site_service.get_site(site_id)
        form = SiteForm(obj=site)

        if form.validate_on_submit():
            try:
                data = {
                    'name': form.name.data,
                    'address': form.address.data,
                    'manager': form.manager.data,
                    'phone': form.phone.data
                }

                site_service.update_site(site_id, data)
                flash('Объект обновлен успешно!', 'success')
                return redirect(url_for('site_bp.sites_list'))

            except ValueError as e:
                flash(f'Ошибка валидации: {str(e)}', 'error')
            except Exception as e:
                logger.error(f"Error updating site {site_id}: {e}")
                flash('Ошибка обновления объекта', 'error')

        return render_template('site_form.html', form=form, title='Редактировать объект')

    except Exception as e:
        logger.error(f"Error loading site {site_id} for editing: {e}")
        flash('Объект не найден', 'error')
        return redirect(url_for('site_bp.sites_list'))

@site_bp.route('/site/<int:site_id>/delete', methods=['POST'])
def delete_site(site_id):
    """Delete site"""
    try:
        site_service.delete_site(site_id)
        flash('Объект удален успешно!', 'success')
    except Exception as e:
        logger.error(f"Error deleting site {site_id}: {e}")
        flash('Ошибка удаления объекта', 'error')

    return redirect(url_for('site_bp.sites_list'))

