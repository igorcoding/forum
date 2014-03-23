from forumApi.api import user
from forumApi.api.helpers.common_helper import *
from forumApi.api.helpers.user_helper import get_id_by_email


def create(ds, **kwargs):
    required(['name', 'short_name', 'user'], kwargs)

    user_id = get_id_by_email(ds, kwargs['user'])

    db = ds.get_db()
    c = db.cursor()
    c.execute("""INSERT INTO forum (name, short_name, user, user_id)
                 VALUES (%s, %s, %s, %s)""",
              (kwargs['name'], kwargs['short_name'], kwargs['user'], user_id))
    db.commit()
    c.close()
    ds.close_last()

    return details(ds, forum=kwargs['short_name'])


def details(ds, **kwargs):
    required(['forum'], kwargs)
    optional('related', kwargs, [], ['user'])

    db = ds.get_db()
    c = db.cursor()
    c.execute("""SELECT * FROM forum
               WHERE forum.short_name = %s""", (kwargs['forum'],))
    forum_data = c.fetchone()
    c.close()
    ds.close_last()

    email = forum_data['user']
    if 'user' in kwargs['related']:
        user_data = user.details(db, user=email)
    else:
        user_data = email

    del forum_data['user_id']
    forum_data['user'] = user_data

    return forum_data


def listPosts(ds, **kwargs):
    pass


def listThreads(ds, **kwargs):
    pass


def listUsers(ds, **kwargs):
    pass

