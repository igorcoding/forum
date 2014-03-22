from forumApi.api import user
from forumApi.api.helpers.common_helper import *
from forumApi.api.helpers.user_helper import get_id_by_email


def create(db, **kwargs):
    required(['name', 'short_name', 'user'], kwargs)

    user_id = get_id_by_email(db, kwargs['user'])
    c = db.cursor()
    c.execute("""INSERT INTO forum (name, short_name, user, user_id)
                 VALUES (%s, %s, %s, %s)""",
              (kwargs['name'], kwargs['short_name'], kwargs['user'], user_id))
    db.commit()
    c.close()

    return details(db, forum=kwargs['short_name'])


def details(db, **kwargs):
    required(['forum'], kwargs)
    optional('related', kwargs, [])

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

    return forum_data


def listPosts(db, **kwargs):
    pass


def listThreads(db, **kwargs):
    pass


def listUsers(db, **kwargs):
    pass

