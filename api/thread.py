import forum
import post
import user
from util.StringBuilder import *
from api.api_helpers.common_helper import *
from api.api_helpers.user_helper import get_id_by_email


def create(ds, **args):
    required(['forum', 'title', 'isClosed', 'user', 'date', 'message', 'slug'], args)
    optional('isDeleted', args, False)

    make_boolean(['isClosed', 'isDeleted'], args)

    # forum_id = get_id_by_short_name(ds, args['forum'])
    # user_id = get_id_by_email(ds, args['user'])

    db = ds.get_db()
    c = db.cursor()
    try:
        c.execute(u"""INSERT INTO thread (forum, title, isClosed, user, date, message, slug, isDeleted)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                  (args['forum'], args['title'], int(args['isClosed']), args['user'],
                   args['date'], args['message'], args['slug'], int(args['isDeleted'])))
        thread_id = db.insert_id()
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        ds.close_last()

    return {
        'id': thread_id,
        'date': args['date'],
        'dislikes': 0,
        'likes': 0,
        'isClosed': args['isClosed'],
        'isDeleted': args['isDeleted'],
        'title': args['title'],
        'slug': args['slug'],
        'message': args['message'],
        'user': args['user'],
        'forum': args['forum'],
        'posts': 0,
        'points': 0
    }


def close(ds, **args):
    required(['thread'], args)

    db = ds.get_db()
    c = db.cursor()

    try:
        c.execute(u"""UPDATE thread
                     SET isClosed = 1
                     WHERE id = %s""",
                  (args['thread'],))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        ds.close_last()

    return {'thread': args['thread']}


def details(ds, **args):
    required(['thread'], args)
    optional('related', args, [], ['user', 'forum'])

    db = ds.get_db()
    c = db.cursor()
    c.execute(u"""SELECT * FROM thread
               WHERE id = %s""", (args['thread'],))
    thread_data = c.fetchone()
    c.close()
    ds.close_last()

    check_empty(thread_data, u"No thread found with that id")

    make_boolean(['isClosed', 'isDeleted'], thread_data)
    thread_data['date'] = str(thread_data['date'])

    # del thread_data['user_id']
    # del thread_data['forum_id']

    if 'user' in args['related']:
        thread_data['user'] = user.details(ds, user=thread_data['user'])

    if 'forum' in args['related']:
        thread_data['forum'] = forum.details(ds, forum=thread_data['forum'])

    return thread_data


def list(ds, orderby='date', **args):
    semi_required(['user', 'forum'], args)
    optional('since', args)
    optional('limit', args)
    optional('order', args, 'desc', ['desc', 'asc'])
    optional('related', args, [], ['user', 'forum'])

    query = StringBuilder()
    query.append(u"""SELECT id FROM thread""")
    params = ()

    if 'user' in args:
        query.append(u"""WHERE user = %s""")
        params += (args['user'],)

    elif 'forum' in args:
        query.append(u"""WHERE forum = %s""")
        params += (args['forum'],)

    if args['since']:
        query.append(u"""AND date >= %s""")
        params += (args['since'],)

    if args['order']:
        query.append(u"""ORDER BY date %s""" % args['order'])

    if args['limit']:
        query.append(u"""LIMIT %d""" % int(args['limit']))

    db = ds.get_db()
    c = db.cursor()
    c.execute(str(query), params)

    threads = [details(ds, thread=row['id'], related=args['related']) for row in c]

    c.close()
    ds.close_last()

    return threads


def listPosts(ds, **args):
    return post.list(ds, **args)


def open(ds, **args):
    required(['thread'], args)

    db = ds.get_db()
    c = db.cursor()
    try:
        c.execute(u"""UPDATE thread
                     SET isClosed = 0
                     WHERE id = %s""",
                  (args['thread'],))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        ds.close_last()

    return {'thread': args['thread']}


def remove(ds, **args):
    required(['thread'], args)

    db = ds.get_db()
    c = db.cursor()
    try:
        c.execute(u"""UPDATE thread
                     SET isDeleted = 1
                     WHERE id = %s""",
                  (args['thread'],))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        ds.close_last()

    return {'thread': args['thread']}


def restore(ds, **args):
    required(['thread'], args)

    db = ds.get_db()
    c = db.cursor()
    try:
        c.execute(u"""UPDATE thread
                     SET isDeleted = 0
                     WHERE id = %s""",
                  (args['thread'],))

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        ds.close_last()

    return {'thread': args['thread']}


def subscribe(ds, **args):
    required(['user', 'thread'], args)

    # user_id = get_id_by_email(ds, args['user'])
    thread_id = args['thread']

    db = ds.get_db()
    c = db.cursor()
    c.execute(u"""SELECT * FROM subscriptions
                 WHERE user = %s AND thread_id = %s""",
              (args['user'], thread_id))
    subscribed = c.fetchone()
    c.close()

    if subscribed:
        query = u"""UPDATE subscriptions SET unsubscribed = 0
                   WHERE user = %s AND thread_id = %s"""
    else:
        query = u"""INSERT INTO subscriptions (user, thread_id)
                   VALUES (%s, %s)"""

    c = db.cursor()
    try:
        c.execute(query, (args['user'], thread_id))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        ds.close_last()

    return {
        'thread': args['thread'],
        'user': args['user']
    }


def unsubscribe(ds, **args):
    required(['user', 'thread'], args)

    # user_id = get_id_by_email(ds, args['user'])
    thread_id = args['thread']

    db = ds.get_db()
    c = db.cursor()
    try:
        c.execute(u"""UPDATE subscriptions SET unsubscribed = 1
                   WHERE user = %s AND thread_id = %s""",
                  (args['user'], thread_id))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        ds.close_last()

    return {
        'thread': args['thread'],
        'user': args['user']
    }


def update(ds, **args):
    required(['message', 'slug', 'thread'], args)

    db = ds.get_db()
    c = db.cursor()
    try:
        c.execute(u"""UPDATE thread
                     SET message = %s,
                         slug = %s
                     WHERE id = %s""",
                  (args['message'], args['slug'], args['thread']))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        ds.close_last()

    return details(ds, thread=args['thread'])


def vote(ds, **args):
    required(['vote', 'thread'], args)
    args['vote'] = int(args['vote'])

    db = ds.get_db()
    c = db.cursor()
    try:
        if args['vote'] > 0:
            c.execute(u"""UPDATE thread
                         SET likes = likes + 1
                         WHERE id = %s""",
                      (args['thread'],))
        elif args['vote'] < 0:
            c.execute(u"""UPDATE thread
                         SET dislikes = dislikes + 1
                         WHERE id = %s""",
                      (args['thread'],))
        else:
            raise Exception(u"Vote is not allowed to be 0")

        c.execute(u"""UPDATE thread
                     SET points = likes - dislikes
                     WHERE id = %s""",
                  (args['thread'],))

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        ds.close_last()

    return details(ds, thread=args['thread'])
