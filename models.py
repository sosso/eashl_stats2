from sqlalchemy import Column, Integer, VARCHAR, INTEGER
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import ForeignKey
import dbutils

engine = create_engine('mysql://b847e1cb77ce40:df22c88c@us-cdbr-east-02.cleardb.com/heroku_13d98724def4930', echo=True, pool_recycle=3600)#recycle connection every hour to prevent overnight disconnect)
Base = declarative_base(bind=engine)
sm = sessionmaker(bind=engine, autoflush=True, autocommit=False, expire_on_commit=False)
Session = scoped_session(sm)

class Player(Base):
    __tablename__ = 'player'
    #column definitions
    id = Column(u'id', INTEGER(), primary_key=True, nullable=False)
    username = Column(u'username', VARCHAR(length=32), nullable=False)

#    item_completions = relationship('ItemCompletion', backref='user') #one to many
    games_played = association_proxy('games_played', 'game')

class GamePlayed(Base):
    __tablename__ = 'gameplayed'

    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id'), primary_key=True)
    file_path = Column(VARCHAR(255))

    user = relationship(Player, backref=backref("games_played", cascade="all, delete-orphan"))

    Game = relationship("Game")

    def __init__(self, user_id, game_id, file_path=None):
        self.user_id = user_id
        self.game_id = game_id
        self.file_path = file_path

    def __repr__(self):
        return '<Gameplayed %d @ %d>' % (self.user_id, self.match_id)


class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer)

    def __init__(self, match_id):
        self.match_id = match_id

    def __repr__(self):
        return '<Game %d>' % self.match_id

    def serialize(self):
        return {'Match id': self.match_id}

Base.metadata.create_all(engine)
