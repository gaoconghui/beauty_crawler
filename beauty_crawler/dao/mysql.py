import logging

from peewee import *

database = MySQLDatabase('beauty', **{'host': 'localhost', 'password': '', 'port': 3306, 'user': 'root'})
database.connect()
logger = logging.getLogger('peewee')
logger.setLevel(logging.INFO)


class BaseModel(Model):
    class Meta:
        database = database

class Gallery(BaseModel):
    insert_time = IntegerField()
    gallery_id = CharField()
    title = CharField()
    domain = CharField()
    tags = CharField()
    from_id = CharField()
    all_page = IntegerField()
    publish_time = IntegerField()

    class Meta:
        db_table = 'gallery'

class Image(BaseModel):
    order = IntegerField()
    image_url = CharField()
    title = CharField()
    desc = CharField()
    gallery_id = CharField()

    class Meta:
        db_table = 'image'
