import user
from forumApi.api import forum
from forumApi.api.helpers.common_helper import *
from forumApi.api.helpers.forum_helper import get_id_by_short_name
from forumApi.api.helpers.user_helper import get_id_by_email


def create(ds, **kwargs):
    required(['forum', 'title', 'isClosed', 'user', 'date', 'message', 'slug'], kwargs)
    optional('isDeleted', kwargs, False)

    forum_id = get_id_by_short_name(ds, kwargs['forum'])
    user_id = get_id_by_email(ds, kwargs['user'])

    db = ds.get_db()
    c = db.cursor()
    c.execute("""INSERT INTO thread (forum, forum_id, title, isClosed, user, user_id, date, message, slug, isDeleted)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
              (kwargs['forum'], forum_id, kwargs['title'], int(kwargs['isClosed']), kwargs['user'],
               user_id, kwargs['date'], kwargs['message'], kwargs['slug'], int(kwargs['isDeleted'])))
    thread_id = c.lastrowid
    db.commit()
    c.close()
    ds.close_last()

    return details(ds, thread=thread_id)


def close(ds, **kwargs):
    required(['thread'], kwargs)

    db = ds.get_db()
    c = db.cursor()
    c.execute("""UPDATE thread
                 SET isClosed = 1
                 WHERE id = %s""",
              (kwargs['thread'],))
    db.commit()
    c.close()
    ds.close_last()

    return {'thread': kwargs['thread']}


def details(ds, **kwargs):
    required(['thread'], kwargs)
    optional('related', kwargs, [], ['user', 'forum'])

    db = ds.get_db()
    c = db.cursor()
    c.execute("""SELECT * FROM thread
               WHERE id = %s""", (kwargs['thread'],))
    thread_data = c.fetchone()
    c.close()
    ds.close_last()

    make_boolean(['isClosed', 'isDeleted'], thread_data)

    del thread_data['user_id']
    del thread_data['forum_id']

    if 'user' in kwargs['related']:
        thread_data['user'] = user.details(ds, user=thread_data['user'])

    if 'forum' in kwargs['related']:
        thread_data['forum'] = forum.details(ds, forum=thread_data['forum'])

    return thread_data


def list(ds, **kwargs):
    pass


def listPosts(ds, **kwargs):
    pass


def open(ds, **kwargs):
    required(['thread'], kwargs)

    db = ds.get_db()
    c = db.cursor()
    c.execute("""UPDATE thread
                 SET isClosed = 0
                 WHERE id = %s""",
              (kwargs['thread'],))
    db.commit()
    c.close()
    ds.close_last()

    return {'thread': kwargs['thread']}


def remove(ds, **kwargs):
    required(['thread'], kwargs)

    db = ds.get_db()
    c = db.cursor()
    c.execute("""UPDATE thread
                 SET isDeleted = 1
                 WHERE id = %s""",
              (kwargs['thread'],))
    db.commit()
    c.close()
    ds.close_last()

    return {'thread': kwargs['thread']}


def restore(ds, **kwargs):
    required(['thread'], kwargs)

    db = ds.get_db()
    c = db.cursor()
    c.execute("""UPDATE thread
                 SET isDeleted = 0
                 WHERE id = %s""",
              (kwargs['thread'],))
    db.commit()
    c.close()
    ds.close_last()

    return {'thread': kwargs['thread']}


def subscribe(ds, **kwargs):
    required(['user', 'thread'], kwargs)

    user_id = get_id_by_email(ds, kwargs['user'])
    thread_id = kwargs['thread']

    db = ds.get_db()
    c = db.cursor()
    c.execute("""SELECT * FROM subscriptions
                 WHERE user_id = %s AND thread_id = %s""",
              (user_id, thread_id))
    subscribed = c.fetchone()
    c.close()

    if subscribed:
        query = """UPDATE subscriptions SET unsubscribed = 0
                   WHERE user_id = %s AND thread_id = %s"""
    else:
        query = """INSERT INTO subscriptions (user_id, thread_id)
                   VALUES (%s, %s)"""

    c = db.cursor()
    c.execute(query, (user_id, thread_id))
    db.commit()
    c.close()
    ds.close_last()

    return {
        'thread': kwargs['thread'],
        'user': kwargs['user']
    }


def unsubscribe(ds, **kwargs):
    required(['user', 'thread'], kwargs)

    user_id = get_id_by_email(ds, kwargs['user'])
    thread_id = kwargs['thread']

    db = ds.get_db()
    c = db.cursor()
    c.execute("""UPDATE subscriptions SET unsubscribed = 1
               WHERE user_id = %s AND thread_id = %s""",
              (user_id, thread_id))
    db.commit()
    c.close()
    ds.close_last()

    return {
        'thread': kwargs['thread'],
        'user': kwargs['user']
    }


def update(ds, **kwargs):
    required(['message', 'slug', 'thread'], kwargs)

    db = ds.get_db()
    c = db.cursor()
    c.execute("""UPDATE thread
                 SET message = %s,
                     slug = %s
                 WHERE id = %s""",
              (kwargs['message'], kwargs['slug'], kwargs['thread']))
    db.commit()
    c.close()
    ds.close_last()

    return details(ds, thread=kwargs['thread'])


def vote(ds, **kwargs):
    pass
