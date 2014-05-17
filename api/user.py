import post
from api.api_helpers.common_helper import *
from api.api_helpers.user_helper import *
from util.StringBuilder import *


def create(ds, **args):
    required(['username', 'name', 'email', 'about'], args)
    optional('isAnonymous', args, False)

    db = ds.get_db()
    c = db.cursor()
    try:
        c.execute(u"""INSERT INTO user (username, name, email, about, isAnonymous, password)
                     VALUES (%s, %s, %s, %s, %s, %s)""",
                  (args['username'], args['name'], args['email'],
                   args['about'], int(args['isAnonymous']), '123456'))
        _id = db.insert_id()

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        ds.close_last()

    user_data = {
        'about': args['about'],
        'email': args['email'],
        'id': _id,
        'isAnonymous': False,
        'name': args['name'],
        'username': args['username']
    }

    return user_data


def details(ds, **args):
    required(['user'], args)

    db = ds.get_db()
    c = db.cursor()
    c.execute(u"""SELECT * FROM user
               WHERE email = %s""", (args['user'],))
    user_data = c.fetchone()
    c.close()

    check_empty(user_data, u"No user found with that email")

    make_boolean(['isAnonymous'], user_data)

    user_data['followers'] = listFollowers(ds, handler=echo_email, user=args['user'])
    user_data['following'] = listFollowing(ds, handler=echo_email, user=args['user'])

    del user_data['password']

    # getting subscriptions
    c = db.cursor()

    c.execute(u"""SELECT thread_id FROM subscriptions
                 WHERE user_id = %s AND unsubscribed = 0""", (user_data['id'],))
    user_data['subscriptions'] = [s['thread_id'] for s in c]

    c.close()
    ds.close_last()

    return user_data


def list_followers_following(ds, who, handler, **args):
    required(['user'], args)
    optional('limit', args)
    optional('order', args, 'desc', ['desc', 'asc'])
    optional('since_id', args)

    possibles = ['follower', 'followee']
    val = 0 if who == 'follower' else 1

    def next_val(v):
        return (v + 1) % len(possibles)

    user_id = get_id_by_email(ds, args['user'])

    query = StringBuilder()
    query.append(u"""SELECT email FROM followers
                    INNER JOIN user ON followers.%s = user.id
                    WHERE %s """ % (possibles[val], possibles[next_val(val)])
                 + u"""= %s AND unfollowed = 0""")

    params = (user_id, )

    if args['since_id']:
        query.append(u"""AND %s """ % (possibles[val],) + u""">= %s""")
        params += (args['since_id'],)

    if args['order']:
        query.append(u"""ORDER BY user.name %s""" % args['order'])

    if args['limit']:
        query.append(u"""LIMIT %d""" % int(args['limit']))

    db = ds.get_db()
    c = db.cursor()
    c.execute(str(query), params)
    # rows = c.fetchall()

    res = [handler(ds, row['email']) for row in c]

    c.close()
    ds.close_last()

    return res


def listFollowers(ds, handler=get_info_by_email, **args):
    return list_followers_following(ds, 'follower', handler, **args)


def listFollowing(ds, handler=get_info_by_email, **args):
    return list_followers_following(ds, 'followee', handler, **args)


def listPosts(ds, **args):
    return post.list(ds, **args)


def follow(ds, **args):
    required(['follower', 'followee'], args)

    follower_id = get_id_by_email(ds, args['follower'])
    followee_id = get_id_by_email(ds, args['followee'])
    params = (follower_id, followee_id)

    db = ds.get_db()
    c = db.cursor()
    c.execute(u"""SELECT * FROM followers
                 WHERE follower = %s AND followee = %s""",
              params)

    in_base_follower = c.fetchone()
    c.close()

    if in_base_follower:
        query = u"""UPDATE followers SET unfollowed = 0
                   WHERE follower = %s AND followee = %s"""
    else:
        query = u"""INSERT INTO followers (follower, followee)
                   VALUES (%s, %s)"""

    c = db.cursor()
    try:
        c.execute(query, params)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        ds.close_last()

    return details(ds, user=args['follower'])


def unfollow(ds, **args):
    required(['follower', 'followee'], args)

    follower_id = get_id_by_email(ds, args['follower'])
    followee_id = get_id_by_email(ds, args['followee'])
    params = (follower_id, followee_id)

    db = ds.get_db()
    c = db.cursor()
    try:
        c.execute(u"""UPDATE followers SET unfollowed=1
                     WHERE follower = %s AND followee = %s""",
                  params)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        ds.close_last()

    return details(ds, user=args['follower'])


def updateProfile(ds, **args):
    required(['about', 'user', 'name'], args)

    db = ds.get_db()
    c = db.cursor()

    try:
        c.execute(u"""UPDATE user
                     SET about = %s,
                         name = %s
                     WHERE email = %s""",
                  (args['about'], args['name'], args['user']))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        ds.close_last()

    return details(ds, user=args['user'])
