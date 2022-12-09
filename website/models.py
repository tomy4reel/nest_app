'''
from website import db, login_manager
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id: int):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    #username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    def __repr__(self):
        return f"{self.id}. {self.username}, {self.email}"


class Price(db.Model):
    __tablename__   = 'prices'
    
    price_id = db.Column(db.Integer, primary_key=True)
    open     = db.Column(db.Float(200))
    low     = db.Column(db.Float(200))
    high     = db.Column(db.Float(200))
    market_cap     = db.Column(db.Float(200))
    market_cap_global     = db.Column(db.Float(200))
    percent_change_24h     = db.Column(db.Float(200))
    close     = db.Column(db.Float(200))
    date_created    = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Price %r>' % self.price_id

db.create_all()
db.session.commit()

'''