import forum
from forumApi.util.StringBuilder import StringBuilder
import thread
import user
from forumApi.api.helpers.common_helper import required, optional, make_boolean, semi_required
from forumApi.api.helpers.user_helper import get_id_by_email


def create(ds, **args):
    required(['date', 'thread', 'message', 'user', 'forum'], args)
    optional('parent', args)
    optional('isApproved', args, False)
    optional('isHighlighted', args, False)
    optional('isEdited', args, False)
    optional('isSpam', args, False)
    optional('isDeleted', args, False)

    user_id = get_id_by_email(ds, args['user'])

    db = ds.get_db()
    c = db.cursor()
    c.execute("""INSERT INTO post (date, thread_id, message, user, user_id, forum, parent,
                                   isApproved, isHighlighted, isEdited, isSpam, isDeleted)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
              (args['date'], args['thread'], args['message'], args['user'], user_id,
               args['forum'], args['parent'], args['isApproved'], args['isHighlighted'],
               args['isEdited'], args['isSpam'], args['isDeleted']))
    post_id = c.lastrowid
    db.commit()
    c.close()
    ds.close_last()

    return details(ds, post=post_id)


def details(ds, **args):
    required(['post'], args)
    optional('related', args, [], ['user', 'thread', 'forum'])

    db = ds.get_db()
    c = db.cursor()
    c.execute("""SELECT * FROM post
               WHERE id = %s""", (args['post'],))
    post_data = c.fetchone()
    c.close()
    ds.close_last()

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
    optional('related', args, [], ['user', 'forum'])

    query = StringBuilder()
    query.append("""SELECT id FROM post""")
    params = ()

    if 'forum' in args:
        query.append("""WHERE forum = %s""")
        params += (args['forum'],)

    elif 'thread' in args:
        query.append("""WHERE thread_id = %s""")
        params += (args['thread'],)

    elif 'user' in args:
        query.append("""WHERE user = %s""")
        params += (args['user'],)

    if args['since']:
        query.append("""WHERE date >= %s""")
        params += (args['since'],)

    if args['order']:
        query.append("""ORDER BY %s """ + args['order'])
        params += (orderby,)

    if args['limit']:
        query.append("""LIMIT %d""" % int(args['limit']))

    db = ds.get_db()
    c = db.cursor()
    c.execute(str(query), params)

    posts = []
    for row in c:
        posts.append(details(ds, post=row['id'], related=args['related']))

    c.close()
    ds.close_last()

    return posts


def remove(ds, **args):
    required(['post'], args)

    # TODO: removing nested posts
    db = ds.get_db()
    c = db.cursor()
    c.execute("""UPDATE post
                 SET isDeleted = 1
                 WHERE id = %s""",
              (args['post'],))
    db.commit()
    c.close()
    ds.close_last()

    return {'post': args['post']}


def restore(ds, **args):
    required(['post'], args)

    db = ds.get_db()
    c = db.cursor()
    c.execute("""UPDATE post
                 SET isDeleted = 0
                 WHERE id = %s""",
              (args['post'],))
    db.commit()
    c.close()
    ds.close_last()

    return {'post': args['post']}


def update(ds, **args):
    required(['message', 'post'], args)

    db = ds.get_db()
    c = db.cursor()
    c.execute("""UPDATE post
                 SET message = %s
                 WHERE id = %s""",
              (args['message'], args['post']))
    db.commit()
    c.close()
    ds.close_last()

    return details(ds, post=int(args['post']))


def vote(ds, **args):
    pass