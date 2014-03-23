from forumApi.util.StringBuilder import StringBuilder
import thread as threads
import user
import post as posts
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
    return posts.list(ds, **kwargs)


def listThreads(ds, **kwargs):
    return threads.list(ds, **kwargs)


def listUsers(ds, **kwargs):
    required(['forum'], kwargs)
    optional('since_id', kwargs)
    optional('limit', kwargs)
    optional('order', kwargs, 'desc', ['desc', 'asc'])

    query = StringBuilder()
    query.append("""SELECT user FROM post
                    WHERE forum = %s""")
    params = (kwargs['forum'],)

    if kwargs['since']:
        query.append("""WHERE date >= %s""")
        params += (kwargs['since'],)

    if kwargs['order']:
        query.append("""ORDER BY date %s""") % kwargs['order']

    if kwargs['limit']:
        query.append("""LIMIT %s""") % kwargs['limit']

    db = ds.get_db()
    c = db.cursor()
    c.execute(str(query), params)

    users_list = [details(ds, user=u['user']) for u in c]

    c.close()
    ds.close_last()

    return users_list


