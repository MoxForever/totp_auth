from ..connection import DatabaseConnection

from .server import ServerDAO
from .user import UserDAO


class DAO(ServerDAO, UserDAO):
    def __init__(self, db: DatabaseConnection):
        self.conn = db
