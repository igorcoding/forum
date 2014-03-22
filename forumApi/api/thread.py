from forumApi.api.helpers.common_helper import *
from forumApi.api.helpers.forum_helper import get_id_by_short_name
from forumApi.api.helpers.user_helper import get_id_by_email


def create(db, **kwargs):
    required(['forum', 'title', 'isClosed', 'user', 'date', 'message', 'slug'], kwargs)
    optional('isDeleted', kwargs, False)
    kwargs['isClosed'] = False if kwargs['isClosed'] == 'False' else True

    forum_id = get_id_by_short_name(db, kwargs['forum'])
    user_id = get_id_by_email(db, kwargs['user'])
    c = db.cursor()
    c.execute("""INSERT INTO thread (forum, forum_id, title, isClosed, user, user_id, date, message, slug, isDeleted)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
              (kwargs['forum'], forum_id, kwargs['title'], int(kwargs['isClosed']), kwargs['user'],
               user_id, kwargs['date'], kwargs['message'], kwargs['slug'], int(kwargs['isDeleted'])))
    thread_id = c.lastrowid
    db.commit()
    c.close()

    return details(db, thread=thread_id)


def close(db, **kwargs):
    required(['thread'], kwargs)

    c = db.cursor()
    c.execute("""UPDATE thread
                 SET isClosed = 1
                 WHERE id = %s""",
              (kwargs['thread'],))
    db.commit()
    c.close()

    return {'thread': kwargs['thread']}


def details(db, **kwargs):
    pass


def list(db, **kwargs):
    pass


def listPosts(db, **kwargs):
    pass


def open(db, **kwargs):
    required(['thread'], kwargs)

    c = db.cursor()
    c.execute("""UPDATE thread
                 SET isClosed = 0
                 WHERE id = %s""",
              (kwargs['thread'],))
    db.commit()
    c.close()

    return {'thread': kwargs['thread']}


def remove(db, **kwargs):
    pass


def restore(db, **kwargs):
    pass


def subscribe(db, **kwargs):
    pass


def unsubscribe(db, **kwargs):
    pass


def update(db, **kwargs):
    pass


def vote(db, **kwargs):
    pass
