from forum import settings

import MySQLdb
import MySQLdb.cursors


class DataService:
    def __init__(self):
        self.host = settings.DATABASES['default']['HOST']
        self.port = int(settings.DATABASES['default']['PORT'])
        self.db_name = settings.DATABASES['default']['NAME']
        self.username = settings.DATABASES['default']['USER']
        self.password = settings.DATABASES['default']['PASSWORD']
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