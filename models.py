from sqlalchemy import (
  Column,
  ForeignKey,
  Integer,
  String,
  DateTime
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """
            Return object data in easily serializeable format
        """
        return {
           'name': self.name,
           'id': self.id,
        }


class CatalogItem(Base):
    __tablename__ = 'catalog_item'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    description = Column(String(250))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    # -- declare foreign keys
    cat_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    # -- declare relationships
    category = relationship(Category)
    user = relationship(User)

    @property
    def serialize(self):
        """
            Return object data in easily serializeable format
        """
        return {
            'cat_id': self.cat_id,
            'description': self.description,
            'id': self.id,
            'title': self.title
        }
    # -- small hacks to grab the category and user names
    @property
    def item_cat_name(self):
        return session.query(Category).\
            filter_by(id=self.cat_id).\
            one().name

    @property
    def item_user_name(self):
        return session.query(User).\
            filter_by(id=self.user_id).\
            one().name


engine = create_engine(
  'sqlite:///catalog_items2.db',
  connect_args={'check_same_thread': False}
)
DBSession = sessionmaker(bind=engine)
session = DBSession()

Base.metadata.create_all(engine)
