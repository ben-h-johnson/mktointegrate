'''
models.py

SQL Alchemy Database Model

Each class below represents a table in our database.  Class attributes of the type
db.Column represent fields.  Attributes of the type db.relationship represent linkages to
other tables (one-to-many or many-to-many relationships).  Please see SQL Alchemy docs for
more information.

http://flask-sqlalchemy.pocoo.org/2.1/

'''
from app import db
from datetime import datetime

#
#  WE CALL THEM 'PEOPLE'
#  aka 'leads', 'contacts', 'customers', 'prospects', 'human beings'
#
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    email = db.Column(db.String(64), unique=True)
    is_customer = db.Column(db.Boolean)
    is_user = db.Column(db.Boolean)
    marketo_lead_id = db.Column(db.Integer)
    orders = db.relationship('Order', backref='person', lazy='dynamic')
    events = db.relationship('Event', backref='person', lazy='dynamic')
    subscriptions = db.relationship('Subscription', secondary=subscriptions,
        backref=db.backref('people', lazy='dynamic'))

    def __init__(self, fname, lname, email, role=None, password=None, language=None):
        self.first_name=fname
        self.last_name=lname
        self.role=role
        self.email = email
        self.language = language if language else 'en'

    def __repr__(self):
        return '<Person %r>' % (self.email)

#
#  ORDERS
#
class Order(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    #When Mapped to the Marketo Opportunity object, this ID will be the Marketo externalOpportunityId
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    cost = db.Column(db.Decimal(precision=2))
    quantity = db.Column(db.Integer)
    date_ordered = db.Column(db.DateTime)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))

    def __repr__(self):
        return '<Order %r, %r @ %r>' % (self.person.email, self.product.name, self.date_ordered.isoformat())

#
#  PRODUCTS (SKUs)
#
class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    sku_code = db.Column(db.String(64))
    srp = db.Column(db.Decimal(precision=2)) #Suggested Retail Price
    description = db.Column(db.String(256))
    orders = db.relationship('Order', backref='product', lazy='dynamic')

#
#  APP TRACKED EVENTS, MILESTONES, EXTRA-MARKETING INTERACTIONS
#
class Event(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    event_date = db.Column(db.DateTime)
    attributes = db.Column(db.String(512)) #JSON Blob with attributes specific to the Event Type
    type_id = db.Column(db.Integer, db.ForeignKey('event_type.id'))

    def __repr__(self):
        return '<Event %r @ %r>' % (self.event_type.name, self.event_date.isoformat())

#
#  EVENT TYPES
#  e.g. 'logged in', 'contacted support'
#
class EventType(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80))
    template = db.Column(db.String(240)) #Pipe delimited List of attribute keys
    events = db.relationship('Event', backref='event_type', lazy='dynamic')

    def __repr__(self):
        return '<EventType %r>' % (self.name)

#
#  JOIN TABLE MATCHING SUBSCRIPTIONS TO PEOPLE
#
subscriptions = db.Table('subscriptions',
    db.Column('person_id', db.Integer, db.ForeignKey('person.id')),
    db.Column('subscription_id', db.Integer, db.ForeignKey('subscription.id'))
)

#
#  SUBSCRIPTIONS
#  e.g. 'Daily Offer Newsletter'
#
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80))
    description = db.Column(db.String(240))
    category = db.Column(db.String(20))

    def __repr__(self):
        return '<Subscription %r>' % (self.name)
