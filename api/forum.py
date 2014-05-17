import post as posts
import user
import thread as threads
from util.StringBuilder import *
from api_helpers.common_helper import *


def create(ds, **args):
    required(['name', 'short_name', 'user'], args)

    db = ds.get_db()
    c = db.cursor()
    try:
        c.execute(u"""INSERT INTO forum (name, short_name, user)
                     VALUES (%s, %s, %s)""",
                  (args['name'], args['short_name'], args['user']))
        _id = db.insert_id()

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        ds.close_last()

    data = {
        'id': _id,
        'name': args['name'],
        'short_name': args['short_name'],
        'user': args['user']
    }

    return data


def details(ds, **args):
    required(['forum'], args)
    optional('related', args, [], ['user'])

    db = ds.get_db()
    c = db.cursor()
    c.execute(u"""SELECT * FROM forum
               WHERE forum.short_name = %s""", (args['forum'],))
    forum_data = c.fetchone()
    c.close()
    ds.close_last()

    check_empty(forum_data, u"No forum found with that short_name")

    email = forum_data['user']
    if 'user' in args['related']:
        user_data = user.details(ds, user=email)
    else:
        user_data = email

    # del forum_data['user_id']
    forum_data['user'] = user_data

    return forum_data


def listPosts(ds, **args):
    return posts.list(ds, **args)


def listThreads(ds, **args):
    return threads.list(ds, **args)


def listUsers(ds, **args):
    required(['forum'], args)
    optional('since_id', args)
    optional('limit', args)
    optional('order', args, 'desc', ['desc', 'asc'])

    query = StringBuilder()
    query.append(u"""SELECT DISTINCT user FROM post
                     INNER JOIN user ON post.user = user.email
                     WHERE post.forum = %s""")
    params = (args['forum'],)

    if args['since_id']:
        query.append(u"""AND user.id >= %s""")
        params += (args['since_id'],)

    if args['order']:
        query.append(u"""ORDER BY user.id %s""" % args['order'])

    if args['limit']:
        query.append(u"""LIMIT %d""" % int(args['limit']))

    db = ds.get_db()
    c = db.cursor()
    c.execute(str(query), params)

    users_list = [user.details(ds, user=u['user']) for u in c]

    c.close()
    ds.close_last()

    return users_list


