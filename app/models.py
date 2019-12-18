from datetime import datetime

from flask import url_for
from flask_login import UserMixin, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login

transaction_certificate = db.Table("transaction_certificate",
                                   db.Column("transaction_id", db.Integer, db.ForeignKey("transaction.id")),
                                   db.Column("certificate_id", db.Integer, db.ForeignKey("certificate.id"))
                                   )


class TimestampMixin:
    time_created = db.Column(db.DateTime, default=datetime.utcnow)
    time_edited = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    profile_pic_filename = db.Column(db.String())

    def profile_pic_url(self):
        if self.profile_pic_filename:
			return self.profile_pic_filename
		else:
			return 'https://x.kinja-static.com/assets/images/logos/placeholders/default.png'
        #     return url_for('uploaded_file', filename=self.profile_pic_filename)
        # else:
        #     return url_for('uploaded_file', filename='default.jpg')

    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))

    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    about = db.Column(db.Text, nullable=True)

    job = db.Column(db.String, nullable=True)

    events_host = db.relationship("Event", backref="seller",
                                  foreign_keys="Event.seller_id")


    def available_events(self):
        return list(filter(lambda x: x.buyer is None, self.events_host))


    events_attend = db.relationship("Event", backref="buyer",
                                    foreign_keys="Event.buyer_id")

    transactions_buyer = db.relationship("Transaction", backref="_from",
                                         foreign_keys="Transaction._from_id")
    transactions_seller = db.relationship("Transaction", backref="_to",
                                          foreign_keys="Transaction._to_id")

    certificates = db.relationship("Certificate", backref="owner", lazy="dynamic")

    def balance(self):
        return self.certificates.count()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def __repr__(self):
        return f"<User@{self.id} {self.username}>"


class Event(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    about = db.Column(db.Text)

    seller_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    buyer_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    time_start = db.Column(db.DateTime)
    time_end = db.Column(db.DateTime)

    pic_filename = db.Column(db.String())

    def pic_url(self):
        fname = "pechka.jpg"
        if self.pic_filename:
            fname = self.pic_filename
        return "https://superawesomevectors.com/wp-content/uploads/2017/09/calendar-outline-free-vector-icon-thumb-275x195.jpg"
        # return url_for("uploaded_file", filename=fname)

    price = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<Event@{self.id} {self.title}>"


class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f"<Cert@{self.id} {self.owner}>"

    @staticmethod
    def available():
        return Certificate.query.filter(Certificate.owner == None)

    @staticmethod
    def unavailable():
        return Certificate.query.filter(Certificate.owner != None)


class Transaction(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    _from_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    _to_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    certificates = db.relationship(
        "Certificate",
        secondary=transaction_certificate,
        primaryjoin=(transaction_certificate.c.transaction_id == id),
        # secondaryjoin=(transaction_certificate.c.transaction_id == id),
        backref=db.backref("transactions")
    )

    def __repr__(self):
        return f"<Transaction@{self.id} {self._from} -> {self._to}>"

    def amount(self):
        return len(self.certificates)


@login.user_loader
def load_user(_id):
    return User.query.get(int(_id))
