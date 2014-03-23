import forum
from forumApi.util.StringBuilder import StringBuilder
import thread
from forumApi.api import user
from forumApi.api.helpers.common_helper import required, optional, make_boolean, semi_required
from forumApi.api.helpers.user_helper import get_id_by_email


def create(ds, **kwargs):
    required(['date', 'thread', 'message', 'user', 'forum'], kwargs)
    optional('parent', kwargs)
    optional('isApproved', kwargs, False)
    optional('isHighlighted', kwargs, False)
    optional('isEdited', kwargs, False)
    optional('isSpam', kwargs, False)
    optional('isDeleted', kwargs, False)

    user_id = get_id_by_email(ds, kwargs['user'])

    db = ds.get_db()
    c = db.cursor()
    c.execute("""INSERT INTO post (date, thread_id, message, user, user_id, forum, parent,
                                   isApproved, isHighlighted, isEdited, isSpam, isDeleted)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
              (kwargs['date'], kwargs['thread'], kwargs['message'], kwargs['user'], user_id,
               kwargs['forum'], kwargs['parent'], kwargs['isApproved'], kwargs['isHighlighted'],
               kwargs['isEdited'], kwargs['isSpam'], kwargs['isDeleted']))
    post_id = c.lastrowid
    db.commit()
    c.close()
    ds.close_last()

    return details(ds, post=post_id)


def details(ds, **kwargs):
    required(['post'], kwargs)
    optional('related', kwargs, [], ['user', 'thread', 'forum'])

    db = ds.get_db()
    c = db.cursor()
    c.execute("""SELECT * FROM post
               WHERE id = %s""", (kwargs['post'],))
    post_data = c.fetchone()
    c.close()
    ds.close_last()

    make_boolean(['isApproved', 'isDeleted', 'isEdited',
                  'isHighlighted', 'isSpam'], post_data)

    thread_id = post_data['thread_id']
    del post_data['user_id']
    del post_data['thread_id']

    if 'user' in kwargs['related']:
        post_data['user'] = user.details(ds, user=post_data['user'])

    if 'thread' in kwargs['related']:
        post_data['thread'] = thread.details(ds, thread=thread_id)
    else:
        post_data['thread'] = thread_id

    if 'forum' in kwargs['related']:
        post_data['forum'] = forum.details(ds, forum=post_data['forum'])

    return post_data


def list(ds, **kwargs):
    semi_required(['forum', 'thread'], kwargs)
    optional('since', kwargs)
    optional('limit', kwargs)
    optional('order', kwargs, 'desc', ['desc', 'asc'])

    query = StringBuilder()
    query.append("""SELECT id FROM post""")
    params = ()

    if 'forum' in kwargs:
        query.append("""WHERE forum = %s""")
        params += kwargs['forum']

    elif 'thread' in kwargs:
        query.append("""WHERE thread_id = %s""")
        params += kwargs['thread']

    if kwargs['since']:
        query.append("""WHERE date >= %s""")
        params += kwargs['since']

    if kwargs['order']:
        query.append("""ORDER BY date %s""")
        params += kwargs['order']

    if kwargs['limit']:
        query.append("""LIMIT %s""")
        params += kwargs['limit']

    db = ds.get_db()
    c = db.cursor()
    c.execute(str(query), params)

    posts = []
    for row in c:
        posts.append(details(ds, post=row['id']))

    c.close()
    ds.close_last()

    return posts


def remove(ds, **kwargs):
    required(['post'], kwargs)

    db = ds.get_db()
    c = db.cursor()
    c.execute("""UPDATE post
                 SET isDeleted = 1
                 WHERE id = %s""",
              (kwargs['post'],))
    db.commit()
    c.close()
    ds.close_last()

    return {'post': kwargs['post']}


def restore(ds, **kwargs):
    required(['post'], kwargs)

    db = ds.get_db()
    c = db.cursor()
    c.execute("""UPDATE post
                 SET isDeleted = 0
                 WHERE id = %s""",
              (kwargs['post'],))
    db.commit()
    c.close()
    ds.close_last()

    return {'post': kwargs['post']}


def update(ds, **kwargs):
    required(['message', 'post'], kwargs)

    db = ds.get_db()
    c = db.cursor()
    c.execute("""UPDATE post
                 SET message = %s
                 WHERE id = %s""",
              (kwargs['message'], kwargs['post']))
    db.commit()
    c.close()
    ds.close_last()

    return details(ds, post=int(kwargs['post']))


def vote(ds, **kwargs):
    pass