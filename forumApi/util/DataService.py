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
        self.db = None

        self.connect()

    def connect(self):
        self.db = MySQLdb.connect(host=self.host,
                                  port=self.port,
                                  db=self.db_name,
                                  user=self.username,
                                  passwd=self.password,
                                  cursorclass=MySQLdb.cursors.SSDictCursor)

    def disconnect(self):
        self.db.close()