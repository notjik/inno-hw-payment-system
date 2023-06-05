import datetime
import sqlalchemy

from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase


class Skins(SqlAlchemyBase):
    __tablename__ = 'skins'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.Text)
    price = sqlalchemy.Column(sqlalchemy.Double, nullable=False)
    image = sqlalchemy.Column(sqlalchemy.String)
    is_buy = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    create_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    users = relationship('Users', secondary='users_skins', back_populates='skins')

    def __repr__(self):
        return '<Skin> [{}] {}'.format(self.id, self.title)