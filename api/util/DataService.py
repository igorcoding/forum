import MySQLdb
import MySQLdb.cursors


class DataService:
    def __init__(self, config_file='api/db.ini'):
        config = DataService.parse_config(config_file)

        self.host = config['host']
        self.port = int(config['port'])
        self.db_name = config['database']
        self.username = config['username']
        self.password = config['password']
        self.opened_connections = []

    @staticmethod
    def parse_config(config_file):
        from ConfigParser import ConfigParser
        config = ConfigParser()
        config.read(config_file)
        section = 'Connection'

        res = {}
        options = config.options(section)
        for option in options:
            try:
                res[option] = config.get(section, option)
            except:
                print "exception on %s!" % option
                res[option] = None
        return res

    def connect(self):
        db = MySQLdb.connect(host=self.host,
                             port=self.port,
                             db=self.db_name,
                             user=self.username,
                             passwd=self.password,
                             cursorclass=MySQLdb.cursors.SSDictCursor,
                             charset='utf8')
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