import __builtin__
import forum
import thread
import user
from util.StringBuilder import *
from api.api_helpers.common_helper import required, optional, make_boolean, semi_required, check_empty, date_to_str
from api.api_helpers.user_helper import get_id_by_email


def create(ds, **args):
    required(['date', 'thread', 'message', 'user', 'forum'], args)
    optional('parent', args, None)
    optional('isApproved', args, False)
    optional('isHighlighted', args, False)
    optional('isEdited', args, False)
    optional('isSpam', args, False)
    optional('isDeleted', args, False)

    user_id = get_id_by_email(ds, args['user'])

    #ds.close_all()
    conn = ds.get_db()
    db = conn['conn']
    c = db.cursor()
    try:
        c.execute(u"""INSERT INTO post (date, thread_id, message, user, user_id, forum, parent,
                                       isApproved, isHighlighted, isEdited, isSpam, isDeleted)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                  (args['date'], args['thread'], args['message'], args['user'], user_id, args['forum'], args['parent'],
                   int(args['isApproved']), int(args['isHighlighted']), int(args['isEdited']), int(args['isSpam']), int(args['isDeleted'])))

        post_id = db.insert_id()

        c.execute(u"""UPDATE thread SET posts = posts + 1
                     WHERE id = %s""", (args['thread'],))

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        db.close() #ds.close(conn['id'])

    data = {
        'date': args['date'],
        'forum': args['forum'],
        'id': post_id,
        'isApproved': args['isApproved'],
        'isDeleted': args['isDeleted'],
        'isEdited': args['isEdited'],
        'isHighlighted': args['isHighlighted'],
        'isSpam': args['isSpam'],
        'message': args['message'],
        'thread': args['thread'],
        'user': args['user']
    }

    return data


def details(ds, **args):
    required(['post'], args)
    optional('related', args, [], ['user', 'thread', 'forum'])

    conn = ds.get_db()
    db = conn['conn']
    c = db.cursor()
    c.execute(u"""SELECT * FROM post
               WHERE id = %s""", (args['post'],))
    post_data = c.fetchone()
    c.close()
    db.close() #ds.close(conn['id'])

    check_empty(post_data, u"No post found with that id")

    post_data['date'] = str(post_data['date'])
    make_boolean(['isApproved', 'isDeleted', 'isEdited',
                  'isHighlighted', 'isSpam'], post_data)

    thread_id = post_data['thread_id']
    del post_data['user_id']
    del post_data['thread_id']

    if 'user' in args['related']:
        post_data['user'] = user.details(ds, user=post_data['user'])

    if 'thread' in args['related']:
        post_data['thread'] = thread.details(ds, thread=thread_id)
    else:
        post_data['thread'] = thread_id

    if 'forum' in args['related']:
        post_data['forum'] = forum.details(ds, forum=post_data['forum'])

    return post_data


def list(ds, orderby='date', **args):
    semi_required(['forum', 'thread', 'user'], args)
    optional('since', args)
    optional('limit', args)
    optional('order', args, 'desc', ['desc', 'asc'])
    optional('related', args, [], ['user', 'forum', 'thread'])

    query = StringBuilder()
    query.append(u"""SELECT * FROM post""")
    params = ()

    if 'thread' in args['related']:
        query.append(u"""INNER JOIN thread ON post.thread_id = thread.id""")
    if 'forum' in args['related']:
        query.append(u"""INNER JOIN forum ON post.forum = forum.short_name""")

    if 'forum' in args:
        query.append(u"""WHERE post.forum = %s""")
        params += (args['forum'],)

    elif 'thread' in args:
        query.append(u"""WHERE post.thread_id = %s""")
        params += (args['thread'],)

    elif 'user' in args:
        query.append(u"""WHERE post.user = %s""")
        params += (args['user'],)

    if args['since']:
        query.append(u"""AND post.date >= %s""")
        params += (args['since'],)

    if args['order']:
        query.append(u"""ORDER BY post.date %s""" % args['order'])

    if args['limit']:
        query.append(u"""LIMIT %d""" % int(args['limit']))

    conn = ds.get_db()
    db = conn['conn']
    c = db.cursor()
    c.execute(str(query), params)
    posts = c.fetchall()

    c.close()
    db.close() #ds.close(conn['id'])

    posts = __builtin__.list(posts)

    for post in posts:
        if 'forum' in args['related']:
            post['forum'] = {
                'id': post['forum.id'],
                'name': post['name'],
                'short_name': post['short_name'],
                'user': post['forum.user'],
            }

            del post['forum.id']
            del post['name']
            del post['short_name']
            del post['forum.user']
            del post['forum.user_id']

        if 'thread' in args['related']:
            post['thread'] = {
                'id': post['thread.id'],
                'date': date_to_str(post['thread.date']),
                'isClosed': post['isClosed'],
                'isDeleted': post['thread.isDeleted'],
                'title': post['title'],
                'slug': post['slug'],
                'posts': post['posts'],
                'message': post['thread.message'],
                'dislikes': post['thread.dislikes'],
                'likes': post['thread.likes'],
                'points': post['thread.points'],
                'user': post['thread.user'],
                'forum': post['thread.forum']
            }

            del post['thread.id']
            del post['thread.date']
            del post['isClosed']
            del post['thread.isDeleted']
            del post['title']
            del post['slug']
            del post['posts']
            del post['thread.message']
            del post['thread.dislikes']
            del post['thread.likes']
            del post['thread.points']
            del post['thread.user']
            del post['thread.forum']
        else:
            post['thread'] = post['thread_id']

        del post['user_id']
        del post['thread_id']
        post['date'] = date_to_str(post['date'])

        if 'user' in args['related']:
            post['user'] = user.details(ds, user=post['user'])

    # posts = [details(ds, post=row['id'], related=args['related']) for row in c]

    return posts


def remove(ds, **args):
    required(['post'], args)

    #ds.close_all()
    conn = ds.get_db()
    db = conn['conn']
    c = db.cursor()
    try:
        c.execute(u"""UPDATE post
                     SET isDeleted = 1
                     WHERE id = %s""",
                  (args['post'],))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        db.close() #ds.close(conn['id'])

    return {'post': args['post']}


def restore(ds, **args):
    required(['post'], args)

    #ds.close_all()
    conn = ds.get_db()
    db = conn['conn']
    c = db.cursor()
    try:
        c.execute(u"""UPDATE post
                     SET isDeleted = 0
                     WHERE id = %s""",
                  (args['post'],))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        db.close() #ds.close(conn['id'])

    return {'post': args['post']}


def update(ds, **args):
    required(['message', 'post'], args)

    #ds.close_all()
    conn = ds.get_db()
    db = conn['conn']
    c = db.cursor()
    try:
        c.execute(u"""UPDATE post
                     SET message = %s
                     WHERE id = %s""",
                  (args['message'], args['post']))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        db.close() #ds.close(conn['id'])

    return details(ds, post=int(args['post']))


def vote(ds, **args):
    required(['vote', 'post'], args)
    args['vote'] = int(args['vote'])

    #ds.close_all()
    conn = ds.get_db()
    db = conn['conn']
    c = db.cursor()
    try:
        if args['vote'] > 0:
            c.execute(u"""UPDATE post
                         SET likes = likes + 1
                         WHERE id = %s""",
                      (args['post'],))
        elif args['vote'] < 0:
            c.execute(u"""UPDATE post
                         SET dislikes = dislikes + 1
                         WHERE id = %s""",
                      (args['post'],))
        else:
            raise Exception(u"Vote is not allowed to be 0")

        c.execute(u"""UPDATE post
                     SET points = likes - dislikes
                     WHERE id = %s""",
                  (args['post'],))

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        db.close() #ds.close(conn['id'])

    return details(ds, post=args['post'])