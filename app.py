from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from wtforms import Form, StringField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///supply_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модели данных
class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ConstructionSite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    manager = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SupplyRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    material_name = db.Column(db.String(100))
    quantity = db.Column(db.String(50))
    unit = db.Column(db.String(20))
    priority = db.Column(db.String(20), default='Средний')  # Низкий, Средний, Высокий, Критический
    status = db.Column(db.String(20), default='Новая')  # Новая, В работе, Ожидает поставки, Выполнена, Отменена
    budget = db.Column(db.Float)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    site_id = db.Column(db.Integer, db.ForeignKey('construction_site.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deadline = db.Column(db.Date)
    notes = db.Column(db.Text)
    
    supplier = db.relationship('Supplier', backref='requests')
    site = db.relationship('ConstructionSite', backref='requests')

class RequestUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('supply_request.id'))
    status = db.Column(db.String(20))
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    request = db.relationship('SupplyRequest', backref='updates')

# Формы
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
    ])
    status = SelectField('Статус', choices=[
        ('Новая', 'Новая'),
        ('В работе', 'В работе'),
        ('Ожидает поставки', 'Ожидает поставки'),
        ('Выполнена', 'Выполнена'),
        ('Отменена', 'Отменена')
    ])
    budget = StringField('Бюджет')
    supplier_id = SelectField('Поставщик', coerce=int)
    site_id = SelectField('Объект', coerce=int)
    deadline = DateField('Срок выполнения')
    notes = TextAreaField('Заметки')

class SupplierForm(Form):
    name = StringField('Название поставщика', validators=[DataRequired()])
    contact_person = StringField('Контактное лицо')
    phone = StringField('Телефон')
    email = StringField('Email')
    address = TextAreaField('Адрес')

class SiteForm(Form):
    name = StringField('Название объекта', validators=[DataRequired()])
    address = TextAreaField('Адрес')
    manager = StringField('Менеджер')
    phone = StringField('Телефон')

# Маршруты
@app.route('/')
def index():
    requests = SupplyRequest.query.order_by(SupplyRequest.created_at.desc()).limit(10).all()
    stats = {
        'total': SupplyRequest.query.count(),
        'new': SupplyRequest.query.filter_by(status='Новая').count(),
        'in_progress': SupplyRequest.query.filter_by(status='В работе').count(),
        'waiting': SupplyRequest.query.filter_by(status='Ожидает поставки').count(),
        'completed': SupplyRequest.query.filter_by(status='Выполнена').count()
    }
    return render_template('index.html', requests=requests, stats=stats)

@app.route('/requests')
def requests_list():
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    
    query = SupplyRequest.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    
    requests = query.order_by(SupplyRequest.created_at.desc()).all()
    return render_template('requests.html', requests=requests, today=date.today())

@app.route('/request/new', methods=['GET', 'POST'])
def new_request():
    form = SupplyRequestForm()
    form.supplier_id.choices = [(s.id, s.name) for s in Supplier.query.all()]
    form.site_id.choices = [(s.id, s.name) for s in ConstructionSite.query.all()]
    
    if form.validate_on_submit():
        request_obj = SupplyRequest(
            title=form.title.data,
            description=form.description.data,
            material_name=form.material_name.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            priority=form.priority.data,
            status=form.status.data,
            budget=float(form.budget.data) if form.budget.data else None,
            supplier_id=form.supplier_id.data if form.supplier_id.data else None,
            site_id=form.site_id.data if form.site_id.data else None,
            deadline=form.deadline.data,
            notes=form.notes.data
        )
        db.session.add(request_obj)
        db.session.commit()
        flash('Заявка создана успешно!', 'success')
        return redirect(url_for('requests_list'))
    
    return render_template('request_form.html', form=form, title='Новая заявка')

@app.route('/request/<int:request_id>')
def request_detail(request_id):
    request_obj = SupplyRequest.query.get_or_404(request_id)
    return render_template('request_detail.html', request=request_obj, today=date.today())

@app.route('/request/<int:request_id>/edit', methods=['GET', 'POST'])
def edit_request(request_id):
    request_obj = SupplyRequest.query.get_or_404(request_id)
    form = SupplyRequestForm(obj=request_obj)
    form.supplier_id.choices = [(s.id, s.name) for s in Supplier.query.all()]
    form.site_id.choices = [(s.id, s.name) for s in ConstructionSite.query.all()]
    
    if form.validate_on_submit():
        request_obj.title = form.title.data
        request_obj.description = form.description.data
        request_obj.material_name = form.material_name.data
        request_obj.quantity = form.quantity.data
        request_obj.unit = form.unit.data
        request_obj.priority = form.priority.data
        request_obj.status = form.status.data
        request_obj.budget = float(form.budget.data) if form.budget.data else None
        request_obj.supplier_id = form.supplier_id.data if form.supplier_id.data else None
        request_obj.site_id = form.site_id.data if form.site_id.data else None
        request_obj.deadline = form.deadline.data
        request_obj.notes = form.notes.data
        
        db.session.commit()
        flash('Заявка обновлена успешно!', 'success')
        return redirect(url_for('request_detail', request_id=request_id))
    
    return render_template('request_form.html', form=form, title='Редактировать заявку')

@app.route('/request/<int:request_id>/update_status', methods=['POST'])
def update_status(request_id):
    request_obj = SupplyRequest.query.get_or_404(request_id)
    new_status = request.form.get('status')
    comment = request.form.get('comment', '')
    
    if new_status and new_status != request_obj.status:
        request_obj.status = new_status
        update = RequestUpdate(
            request_id=request_id,
            status=new_status,
            comment=comment
        )
        db.session.add(update)
        db.session.commit()
        flash('Статус обновлен!', 'success')
    
    return redirect(url_for('request_detail', request_id=request_id))

@app.route('/suppliers')
def suppliers_list():
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return render_template('suppliers.html', suppliers=suppliers)

@app.route('/supplier/new', methods=['GET', 'POST'])
def new_supplier():
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier(
            name=form.name.data,
            contact_person=form.contact_person.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data
        )
        db.session.add(supplier)
        db.session.commit()
        flash('Поставщик добавлен успешно!', 'success')
        return redirect(url_for('suppliers_list'))
    
    return render_template('supplier_form.html', form=form, title='Новый поставщик')

@app.route('/sites')
def sites_list():
    sites = ConstructionSite.query.order_by(ConstructionSite.name).all()
    return render_template('sites.html', sites=sites)

@app.route('/site/new', methods=['GET', 'POST'])
def new_site():
    form = SiteForm()
    if form.validate_on_submit():
        site = ConstructionSite(
            name=form.name.data,
            address=form.address.data,
            manager=form.manager.data,
            phone=form.phone.data
        )
        db.session.add(site)
        db.session.commit()
        flash('Объект добавлен успешно!', 'success')
        return redirect(url_for('sites_list'))
    
    return render_template('site_form.html', form=form, title='Новый объект')

@app.route('/api/stats')
def api_stats():
    stats = {
        'total': SupplyRequest.query.count(),
        'new': SupplyRequest.query.filter_by(status='Новая').count(),
        'in_progress': SupplyRequest.query.filter_by(status='В работе').count(),
        'waiting': SupplyRequest.query.filter_by(status='Ожидает поставки').count(),
        'completed': SupplyRequest.query.filter_by(status='Выполнена').count()
    }
    return jsonify(stats)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 