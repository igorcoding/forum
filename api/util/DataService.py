import MySQLdb
import MySQLdb.cursors

from forum import settings


class DataService:
    def __init__(self):
        default_db = settings.DATABASES['default']

        self.host = default_db['HOST']
        self.port = int(default_db['PORT'])
        self.db_name = default_db['NAME']
        self.username = default_db['USER']
        self.password = default_db['PASSWORD']
        self.opened_connections = []

    def connect(self):
        db = MySQLdb.connect(host=self.host,
                             port=self.port,
                             db=self.db_name,
                             user=self.username,
                             passwd=self.password,
                             cursorclass=MySQLdb.cursors.SSDictCursor)
        self.opened_connections.append(db)
        return db

    def get_db(self):
        return self.connect()

    def close_all(self):
        for db in self.opened_connections:
            db.close()
        self.opened_connections = []

    def close_last(self):
        self.opened_connections[-1].close()
        self.opened_connections.pop()