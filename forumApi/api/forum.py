class Forum:
    def __init__(self, data_service):
        self.data_service = data_service
        pass

    def create(self, **kwargs):
        pass

    def details(self, **kwargs):
        if 'forum' not in kwargs:
            raise Exception("forum short_name is required.")
        if 'related' not in kwargs:
            kwargs['related'] = []

        query = """SELECT * FROM forum
                   INNER JOIN user ON forum.user_id = user.id
                   WHERE forum.short_name = '{0}'
                """\
                .format(kwargs['forum'])

        res = self.data_service.query(query)
        row = res.fetch_row(how=1, maxrows=10)
        pass
        #return response_good(result)

    def list_posts(self, **kwargs):
        pass

    def list_threads(self, **kwargs):
        pass

    def list_users(self, **kwargs):
        pass

