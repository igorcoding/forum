from forumApi.api import post
from forumApi.api.helpers.common_helper import *
from forumApi.api.helpers.user_helper import *
from forumApi.util.StringBuilder import StringBuilder


def create(ds, **kwargs):
    required(['username', 'name', 'email', 'about'], kwargs)
    optional('isAnonymous', kwargs, False)

    db = ds.get_db()
    c = db.cursor()
    c.execute("""INSERT INTO user (username, name, email, about, isAnonymous, password)
                 VALUES (%s, %s, %s, %s, %s, %s)""",
              (kwargs['username'], kwargs['name'], kwargs['email'],
               kwargs['about'], int(kwargs['isAnonymous']), '123456'))
    db.commit()
    c.close()

    c = db.cursor()
    c.execute("""SELECT * FROM user
               WHERE email = %s""", (kwargs['email'],))
    user_data = c.fetchone()
    c.close()
    ds.close_last()

    del user_data['password']

    return user_data


def details(ds, **kwargs):
    required(['user'], kwargs)

    db = ds.get_db()
    c = db.cursor()
    c.execute("""SELECT * FROM user
               WHERE email = %s""", (kwargs['user'],))
    user_data = c.fetchone()
    c.close()

    make_boolean(['isAnonymous'], user_data)

    user_data['followers'] = listFollowers(ds, handler=get_email_by_id, user=kwargs['user'])
    user_data['followees'] = listFollowing(ds, handler=get_email_by_id, user=kwargs['user'])

    del user_data['password']

    # getting subscriptions
    c = db.cursor()

    c.execute("""SELECT thread_id FROM subscriptions
                 WHERE user_id = %s""", (user_data['id'],))
    user_data['subscriptions'] = [s['thread_id'] for s in c]

    c.close()
    ds.close_last()

    return user_data


def list_followers_followees(ds, who, handler=get_info_by_id, **kwargs):
    required(['user'], kwargs)
    optional('limit', kwargs)
    optional('order', kwargs, 'desc', ['desc', 'asc'])
    optional('since_id', kwargs)

    possibles = ['follower', 'followee']
    val = 0 if who == 'follower' else 1

    def next_val(v):
        return (v + 1) % len(possibles)

    user_id = get_id_by_email(ds, kwargs['user'])

    query = StringBuilder()
    query.append("""SELECT %s FROM followers
                    INNER JOIN user ON followers.%s = user.id
                    WHERE %s """ % (possibles[val], possibles[val], possibles[next_val(val)])
                 + """= %s AND unfollowed = 0""")

    params = (user_id, )

    if kwargs['since_id']:
        query.append("""AND %s""" % (possibles[val],) + """>= %s""")
        params += (kwargs['since_id'],)

    if kwargs['order']:
        query.append("""ORDER BY user.name %s""" % kwargs['order'])

    if kwargs['limit']:
        query.append("""LIMIT %d""" % int(kwargs['limit']))

    db = ds.get_db()
    c = db.cursor()
    c.execute(str(query), params)

    res = [handler(ds, row[possibles[val]]) for row in c]

    c.close()
    ds.close_last()

    return res


def listFollowers(ds, handler=get_info_by_id, **kwargs):
    return list_followers_followees(ds, 'follower', handler, **kwargs)


def listFollowing(ds, handler=get_info_by_id, **kwargs):
    return list_followers_followees(ds, 'followee', handler, **kwargs)


def listPosts(ds, **kwargs):
    # TODO: date parameter problem
    return post.list(ds, **kwargs)


def follow(ds, **kwargs):
    required(['follower', 'followee'], kwargs)

    follower_id = get_id_by_email(ds, kwargs['follower'])
    followee_id = get_id_by_email(ds, kwargs['followee'])
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

    return details(ds, user=kwargs['follower'])


def unfollow(ds, **kwargs):
    required(['follower', 'followee'], kwargs)

    follower_id = get_id_by_email(ds, kwargs['follower'])
    followee_id = get_id_by_email(ds, kwargs['followee'])
    params = (follower_id, followee_id)

    db = ds.get_db()
    c = db.cursor()
    c.execute("""UPDATE followers SET unfollowed=1
                 WHERE follower = %s AND followee = %s""",
              params)
    db.commit()
    c.close()
    ds.close_last()

    return details(ds, user=kwargs['follower'])


def updateProfile(ds, **kwargs):
    required(['about', 'user', 'name'], kwargs)

    db = ds.get_db()
    c = db.cursor()
    c.execute("""UPDATE user
                 SET about = %s,
                     name = %s
                 WHERE email = %s""",
              (kwargs['about'], kwargs['name'], kwargs['user']))
    db.commit()
    c.close()
    ds.close_last()

    return details(ds, user=kwargs['user'])
