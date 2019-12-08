from datetime import datetime

from app import db

transaction_certificate = db.Table("transaction_certificate",
                                   db.Column("transaction_id", db.Integer, db.ForeignKey("transaction.id")),
                                   db.Column("certificate_id", db.Integer, db.ForeignKey("certificate.id"))
                                   )


class TimestampMixin:
    time_created = db.Column(db.DateTime, default=datetime.utcnow)
    time_edited = db.Column(db.DateTime, default=datetime.utcnow)


class User(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    about = db.Column(db.Text, nullable=True)

    events_host = db.relationship("Event", backref="seller", lazy="dynamic",
                                  foreign_keys="Event.seller_id")
    events_attend = db.relationship("Event", backref="buyer", lazy="dynamic",
                                    foreign_keys="Event.buyer_id")

    transactions_buyer = db.relationship("Transaction", backref="_from", lazy="dynamic",
                                         foreign_keys="Transaction._from_id")
    transactions_seller = db.relationship("Transaction", backref="_to", lazy="dynamic",
                                          foreign_keys="Transaction._to_id")

    certificates = db.relationship("Certificate", backref="owner", lazy="dynamic")

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

    cost = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Event@{self.id} {self.title}>"


class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f"<Cert@{self.id} {self.owner}>"


class Transaction(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    _from_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    _to_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    certificates = db.relationship(
        "Certificate",
        secondary=transaction_certificate,
        primaryjoin=(transaction_certificate.c.transaction_id == id),
        secondaryjoin=(transaction_certificate.c.transaction_id == id),
        backref=db.backref("transactions", lazy="dynamic"), lazy="dynamic"
    )

    def __repr__(self):
        return f"<Transaction@{self.id} {self._from} -> {self._to}>"

    def amount(self):
        return self.certificates.count()
