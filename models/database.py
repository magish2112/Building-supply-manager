from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Supplier(db.Model):
    __tablename__ = 'supplier'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    requests = db.relationship('SupplyRequest', back_populates='supplier', lazy='dynamic')

    def __repr__(self):
        return f'<Supplier {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ConstructionSite(db.Model):
    __tablename__ = 'construction_site'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    manager = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    requests = db.relationship('SupplyRequest', back_populates='site', lazy='dynamic')

    def __repr__(self):
        return f'<ConstructionSite {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'manager': self.manager,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SupplyRequest(db.Model):
    __tablename__ = 'supply_request'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    material_name = db.Column(db.String(100))
    quantity = db.Column(db.String(50))
    unit = db.Column(db.String(20))
    priority = db.Column(db.String(20), default='Средний')
    status = db.Column(db.String(20), default='Новая')
    budget = db.Column(db.Float)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)
    site_id = db.Column(db.Integer, db.ForeignKey('construction_site.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deadline = db.Column(db.Date)
    notes = db.Column(db.Text)

    # Relationships
    supplier = db.relationship('Supplier', back_populates='requests')
    site = db.relationship('ConstructionSite', back_populates='requests')
    updates = db.relationship('RequestUpdate', back_populates='request', lazy='dynamic', cascade='all, delete-orphan')

    # Status and priority constants
    STATUS_CHOICES = ['Новая', 'В работе', 'Ожидает поставки', 'Выполнена', 'Отменена']
    PRIORITY_CHOICES = ['Низкий', 'Средний', 'Высокий', 'Критический']

    def __repr__(self):
        return f'<SupplyRequest {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'material_name': self.material_name,
            'quantity': self.quantity,
            'unit': self.unit,
            'priority': self.priority,
            'status': self.status,
            'budget': self.budget,
            'supplier_id': self.supplier_id,
            'site_id': self.site_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'notes': self.notes,
            'supplier': self.supplier.to_dict() if self.supplier else None,
            'site': self.site.to_dict() if self.site else None
        }

    def update_status(self, new_status, comment=None):
        """Update request status with history tracking"""
        if new_status not in self.STATUS_CHOICES:
            raise ValueError(f"Invalid status: {new_status}")

        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.utcnow()

        # Create update record
        update = RequestUpdate(
            request_id=self.id,
            status=new_status,
            comment=comment
        )
        db.session.add(update)

        return old_status, new_status

class RequestUpdate(db.Model):
    __tablename__ = 'request_update'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('supply_request.id'), nullable=False)
    status = db.Column(db.String(20))
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    request = db.relationship('SupplyRequest', back_populates='updates')

    def __repr__(self):
        return f'<RequestUpdate {self.request_id} -> {self.status}>'

    def to_dict(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'status': self.status,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

