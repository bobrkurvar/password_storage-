from .crud import Crud
from core import *


db_url = str(conf.DATABASE_URL)
manager = Crud(db_url)
