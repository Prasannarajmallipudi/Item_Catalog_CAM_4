import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class UserData(Base):
    # This class is to create user table,
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    picture = Column(String(255))

    @property
    def serialize(self):
        # Return data as object in simple serializeable format
        return {
            'name': self.name,
            'id': self.id,
            'email': self.email,
            'picture': self.picture,
        }


class Brand(Base):
    # This class is to create brand table,
    __tablename__ = 'brand'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    name = Column(String(50), nullable=False)

    user = relationship(UserData)

    @property
    def serialize(self):
        # Return data as object in simple serializeable format
        return {
            'name': self.name,
            'id': self.id,

        }


class ModelName(Base):
    # This class is to create model table
    __tablename__ = 'model'
    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey('brand.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    modelnumber = Column(String(30))
    colors = Column(String(30))

    price = Column(String(20))
    description = Column(String(500))

    brand = relationship(Brand)
    user = relationship(UserData)

    @property
    def serialize(self):
        # Return data as object in simple serializeable format
        return {

            'id': self.id,

            'modelnumber': self.modelnumber,

            'colors':  self.colors,
            'price': self.price,
            'description': self.description,


        }

engine = create_engine('sqlite:///camcatalog.db')
Base.metadata.create_all(engine)
