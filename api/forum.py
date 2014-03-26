import post as posts
import user
import thread as threads
from util.StringBuilder import *
from helpers.common_helper import *
from helpers.user_helper import get_id_by_email


def create(ds, **args):
    required(['name', 'short_name', 'user'], args)

    user_id = get_id_by_email(ds, args['user'])

    db = ds.get_db()
    c = db.cursor()
    try:
        c.execute("""INSERT INTO forum (name, short_name, user, user_id)
                     VALUES (%s, %s, %s, %s)""",
                  (args['name'], args['short_name'], args['user'], user_id))

        c.execute("""UPDATE thread SET posts = posts + 1""")
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        ds.close_last()

    return details(ds, forum=args['short_name'])


def details(ds, **args):
    required(['forum'], args)
    optional('related', args, [], ['user'])

    db = ds.get_db()
    c = db.cursor()
    c.execute("""SELECT * FROM forum
               WHERE forum.short_name = %s""", (args['forum'],))
    forum_data = c.fetchone()
    c.close()
    ds.close_last()

    check_empty(forum_data, "No forum found with that short_name")

    email = forum_data['user']
    if 'user' in args['related']:
        user_data = user.details(db, user=email)
    else:
        user_data = email

    del forum_data['user_id']
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
    query.append("""SELECT user FROM post
                    WHERE forum = %s""")
    params = (args['forum'],)

    if args['since']:
        query.append("""WHERE date >= %s""")
        params += (args['since'],)

    if args['order']:
        query.append("""ORDER BY date %s""" % args['order'])

    if args['limit']:
        query.append("""LIMIT %d""" % int(args['limit']))

    db = ds.get_db()
    c = db.cursor()
    c.execute(str(query), params)

    users_list = [details(ds, user=u['user']) for u in c]

    c.close()
    ds.close_last()

    return users_list


