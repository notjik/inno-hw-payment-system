import sqlalchemy

from .db_session import SqlAlchemyBase


class UsersSkins(SqlAlchemyBase):
    __tablename__ = 'users_skins'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('users.id'))
    skin_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('skins.id'))

    def __repr__(self):
        return '<UserSkin> [{}] {} - {}'.format(self.id, self.user_id, self.skin_id)
