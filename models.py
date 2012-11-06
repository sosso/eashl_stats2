from sqlalchemy import Column, Integer, VARCHAR, INTEGER
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import BigInteger
import dbutils

engine = create_engine('mysql://b847e1cb77ce40:df22c88c@us-cdbr-east-02.cleardb.com/heroku_13d98724def4930', echo=False, pool_recycle=3600)#recycle connection every hour to prevent overnight disconnect)
Base = declarative_base(bind=engine)
sm = sessionmaker(bind=engine, autoflush=True, autocommit=False, expire_on_commit=False)
Session = scoped_session(sm)

class Player(Base):
    __tablename__ = 'player'
    #column definitions
    id = Column(u'id', INTEGER(), primary_key=True, nullable=False)
    username = Column(u'username', VARCHAR(length=32), nullable=False)

    def __init__(self, username):
        self.username = username

#    item_completions = relationship('ItemCompletion', backref='user') #one to many
    games = association_proxy('games_played', 'game')

class GamePlayed(Base):
    __tablename__ = 'gameplayed'

    player_id = Column(Integer, ForeignKey('player.id'), primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id'), primary_key=True)

    player = relationship(Player, backref=backref("games_played", cascade="all, delete-orphan"))

    Game = relationship("Game")

    def __init__(self, player_id=None, game_id=None):
        self.player_id = player_id
        self.game_id = game_id

    def __repr__(self):
        return '<Gameplayed %d @ %d>' % (self.player_id, self.match_id)


class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    match_id = Column(BigInteger)

    def __init__(self, match_id):
        self.match_id = match_id

    def __repr__(self):
        return '<Game %d>' % self.match_id

    def serialize(self):
        return {'Match id': self.match_id}

Base.metadata.create_all(engine)
