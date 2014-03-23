import time
from forumApi.api import post
from forumApi.api.helpers.common_helper import *
from forumApi.api.helpers.user_helper import *
from forumApi.util.StringBuilder import StringBuilder


def create(ds, **args):
    required(['username', 'name', 'email', 'about'], args)
    optional('isAnonymous', args, False)

    db = ds.get_db()
    c = db.cursor()
    c.execute("""INSERT INTO user (username, name, email, about, isAnonymous, password)
                 VALUES (%s, %s, %s, %s, %s, %s)""",
              (args['username'], args['name'], args['email'],
               args['about'], int(args['isAnonymous']), '123456'))
    db.commit()
    c.close()

    c = db.cursor()
    c.execute("""SELECT * FROM user
               WHERE email = %s""", (args['email'],))
    user_data = c.fetchone()
    c.close()
    ds.close_last()

    del user_data['password']

    return user_data


def details(ds, **args):
    required(['user'], args)

    db = ds.get_db()
    c = db.cursor()
    c.execute("""SELECT * FROM user
               WHERE email = %s""", (args['user'],))
    user_data = c.fetchone()
    c.close()

    make_boolean(['isAnonymous'], user_data)

    user_data['followers'] = listFollowers(ds, handler=get_email_by_id, user=args['user'])
    user_data['followees'] = listFollowing(ds, handler=get_email_by_id, user=args['user'])

    del user_data['password']

    # getting subscriptions
    c = db.cursor()

    c.execute("""SELECT thread_id FROM subscriptions
                 WHERE user_id = %s""", (user_data['id'],))
    user_data['subscriptions'] = [s['thread_id'] for s in c]

    c.close()
    ds.close_last()

    return user_data


def list_followers_followees(ds, who, handler=get_info_by_id, **args):
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
    query.append("""SELECT %s FROM followers
                    INNER JOIN user ON followers.%s = user.id
                    WHERE %s """ % (possibles[val], possibles[val], possibles[next_val(val)])
                 + """= %s AND unfollowed = 0""")

    params = (user_id, )

    if args['since_id']:
        query.append("""AND %s """ % (possibles[val],) + """>= %s""")
        params += (args['since_id'],)

    if args['order']:
        query.append("""ORDER BY user.name %s""" % args['order'])

    if args['limit']:
        query.append("""LIMIT %d""" % int(args['limit']))

    db = ds.get_db()
    c = db.cursor()
    c.execute(str(query), params)

    res = [handler(ds, row[possibles[val]]) for row in c]

    c.close()
    ds.close_last()

    return res


def listFollowers(ds, handler=get_info_by_id, **args):
    time.sleep(5)
    return list_followers_followees(ds, 'follower', handler, **args)


def listFollowing(ds, handler=get_info_by_id, **args):
    return list_followers_followees(ds, 'followee', handler, **args)


def listPosts(ds, **args):
    # TODO: date parameter problem
    # TODO: should be order by name, not by date
    return post.list(ds, **args)


def follow(ds, **args):
    required(['follower', 'followee'], args)

    follower_id = get_id_by_email(ds, args['follower'])
    followee_id = get_id_by_email(ds, args['followee'])
    params = (follower_id, followee_id)

    db = ds.get_db()
    c = db.cursor()
    c.execute("""SELECT * FROM followers
                 WHERE follower = %s AND followee = %s""",
              params)

    in_base_follower = c.fetchone()
    c.close()

    if in_base_follower:
        query = """UPDATE followers SET unfollowed = 0
                   WHERE follower = %s AND followee = %s"""
    else:
        query = """INSERT INTO followers (follower, followee)
                   VALUES (%s, %s)"""

    c = db.cursor()
    c.execute(query, params)
    db.commit()
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
    c.execute("""UPDATE followers SET unfollowed=1
                 WHERE follower = %s AND followee = %s""",
              params)
    db.commit()
    c.close()
    ds.close_last()

    return details(ds, user=args['follower'])


def updateProfile(ds, **args):
    required(['about', 'user', 'name'], args)

    db = ds.get_db()
    c = db.cursor()
    c.execute("""UPDATE user
                 SET about = %s,
                     name = %s
                 WHERE email = %s""",
              (args['about'], args['name'], args['user']))
    db.commit()
    c.close()
    ds.close_last()

    return details(ds, user=args['user'])
