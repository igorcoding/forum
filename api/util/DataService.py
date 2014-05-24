from pprint import pprint
import threading
import MySQLdb
import MySQLdb.cursors
from threading import Timer


class DataService:


    def __init__(self, config_file='api/db.ini'):
        config = DataService._parse_config(config_file)

        self.host = config['host']
        self.port = int(config['port'])
        self.db_name = config['database']
        self.username = config['username']
        self.password = config['password']
        self.opened_connections = []
        self._id = 0
        self._connections_limit = 10

        self._timer_interval = 30.0
        self._timer = None
        self._locker = threading.Lock()

    def _timer_job(self):
        print "Force closing all connections with db"
        self.close_all()

    def _create_timer(self):
        self._timer = Timer(self._timer_interval, self._timer_job)
        self._timer.start()

    def _lock(self):
        if self._timer is not None:
            self._timer.cancel()
        self._locker.acquire()

    def _free(self):
        if self._timer is not None:
            self._timer.cancel()
        self._create_timer()
        self._locker.release()

    @staticmethod
    def _parse_config(config_file):
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

    def truncate(self):
        clears = [
            "set FOREIGN_KEY_CHECKS=0",
            "TRUNCATE TABLE subscriptions",
            "TRUNCATE TABLE followers",
            "TRUNCATE TABLE post",
            "TRUNCATE TABLE thread",
            "TRUNCATE TABLE forum",
            "TRUNCATE TABLE user",
            "set FOREIGN_KEY_CHECKS=1"
        ]
        self.close_all()
        conn = self.get_db()
        db = conn['conn']
        c = db.cursor()
        for statement in clears:
            c.execute(statement)
        c.close()
        self.close(conn['id'])
        self.close_all()


    def connect(self):
        db = MySQLdb.connect(host=self.host,
                             port=self.port,
                             db=self.db_name,
                             user=self.username,
                             passwd=self.password,
                             cursorclass=MySQLdb.cursors.SSDictCursor,
                             charset='utf8')
        db_obj = {
            'id': self._id,
            'conn': db,
            'free': False,
            'forceRemoval': False
        }
        # if self.get_length() >= self._connections_limit:
        #     db_obj['forceRemoval'] = True
        #
        self.opened_connections.append(db_obj)
        # self._id += 1
        return db_obj

    # @synchronous('lock')
    def get_db(self):
        # self._lock()
        #
        # # if len(self.opened_connections) >= self.connections_limit:
        # #     self.close_free()
        # connection = None
        # if self.get_length() == 0:
        #     connection = self.connect()
        # else:
        #     for c in self.opened_connections:
        #         if c is not None and c['free']:
        #             connection = c
        #             c['free'] = False
        #             break
        #     if connection is None:
        #         connection = self.connect()
        #
        # self._free()
        connection = self.connect()
        return connection

    def close_all(self):
        # print self.opened_connections
        for c in self.opened_connections:
            if c is not None and c['free'] is not None:
                c['conn'].close()
        self.opened_connections = []

    # @synchronous('lock')
    def close_free(self):
        # self.opened_connections[-1]['free'] = True
        # self.lock.acquire()
        new_conns = self.opened_connections
        for c in self.opened_connections:
            if c['free']:
                c['conn'].close()
                c['free'] = None
                new_conns.pop(c['id'])
        # print "new_conns length: ", len(new_conns)
        self.opened_connections = new_conns
        # self.lock.release()
        # pprint(self.opened_connections)

    # @synchronous('lock')
    def close(self, conn_id):
        self.opened_connections[-1]['conn'].close()
        self.opened_connections.pop()
        # self._lock()
        # conn = None
        # real_index = None
        # # print "closing %d" % conn_id
        # for i, c in enumerate(self.opened_connections):
        #     if c['id'] == conn_id:
        #         conn = c
        #         real_index = i
        #         break
        # try:
        #     if conn is not None:
        #         if conn['forceRemoval']:
        #             conn['conn'].close()
        #             conn['free'] = None
        #             conn['forceRemoval'] = None
        #             # print '---removing. total: ', self.get_length(), "; id: ", conn_id
        #             self.opened_connections.pop(real_index)
        #             # print 'removing. total: ', self.get_length(), "; id: ", conn_id
        #         else:
        #             conn['free'] = True
        #             # print '@@@not removing. total: ', self.get_length(), "; id: ", conn_id
        #         # self.opened_connections.pop(conn_id - 1)
        #     else:
        #         raise Exception('Connection not found')
        # finally:
        #     self._free()

    def get_length(self):
        return len(self.opened_connections)

    def __post(self, query, params, conn=None):
        self.close_all()
        if conn is None:
            conn = self.get_db()

        db = conn['conn']
        c = db.cursor()
        try:
            c.execute(query, params)
            _id = db.insert_id()
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            c.close()
            self.close(conn['id'])

        return _id

    def __get(self, query, params, ds, db=None):
        pass