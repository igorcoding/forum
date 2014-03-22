from forumApi.api import user
from forumApi.util.helpers import response_good


def create(db, **kwargs):
    pass


def details(db, **kwargs):
    if 'forum' not in kwargs:
        raise Exception("forum short_name is required.")
    if 'related' not in kwargs:
        kwargs['related'] = []

    c = db.cursor()
    c.execute("""SELECT * FROM forum
               WHERE forum.short_name = %s""", (kwargs['forum'],))
    forum_data = c.fetchone()
    c.close()

    email = forum_data['user']
    if 'user' in kwargs['related']:
        user_data = user.details(db, output='raw', user=email)
    else:
        user_data = email

    del forum_data['user_id']
    forum_data['user'] = user_data

    resp = response_good(forum_data)
    return resp


def list_posts(db, **kwargs):
    pass


def list_threads(db, **kwargs):
    pass


def list_users(db, **kwargs):
    pass

