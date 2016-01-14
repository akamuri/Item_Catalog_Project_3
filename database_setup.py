from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
       }


class Game(Base):
    __tablename__ = 'game'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    ageRating = Column(String(800))
    price = Column(String(8))
    image = Column(String(250))
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
           'description'  : self.description,
           'ageRating'    : self.ageRating,
           'price'        : self.price,

       }


class Genre(Base):
    __tablename__ = 'genre'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
       }
 
class Console(Base):
    __tablename__ = 'console'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable=False)


    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'       : self.name,
           'id'         : self.id,
       }

class Inventory(Base):
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable=False)
    game_id = Column(Integer,ForeignKey('game.id'))
    game = relationship(Game)
    console = Column(String(250), nullable=False)
    genre = Column(String(250), nullable=False)
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)



    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
       }



engine = create_engine('sqlite:///gameCatalog.db')
 

Base.metadata.create_all(engine)
