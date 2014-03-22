from forumApi.api.helpers.common_helper import *
from forumApi.api.helpers.user_helper import *


def create(db, **kwargs):
    required(['username', 'name', 'email', 'about'], kwargs)
    optional('isAnonymous', kwargs, False)

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

    return user_data


def details(db, **kwargs):
    required(['user'], kwargs)

    c = db.cursor()
    c.execute("""SELECT * FROM user
               WHERE email = %s""", (kwargs['user'],))
    user_data = c.fetchone()
    c.close()
    user_data['isAnonymous'] = bool(user_data['isAnonymous'])

    user_data['followers'] = listFollowers(db, handler=get_email_by_id, user=kwargs['user'])
    user_data['followees'] = listFollowing(db, handler=get_email_by_id, user=kwargs['user'])

    # getting subscriptions
    c = db.cursor()
    subscriptions = []
    c.execute("""SELECT thread_id FROM subscriptions
                 WHERE user_id = %s""", (user_data['id'],))
    for s in c:
        subscriptions.append(s['thread_id'])
    c.close()

    user_data['subscriptions'] = subscriptions

    return user_data


def follow(db, **kwargs):
    required(['follower', 'followee'], kwargs)

    c = db.cursor()
    c.execute("""SELECT * FROM followers
                 WHERE follower = %s AND followee = %s""",
             (kwargs['follower'], kwargs['followee']))

    in_base_follower = c.fetchone()
    c.close()

    if in_base_follower:
        query = """UPDATE followers SET unfollowed = 0
                   WHERE follower = %s AND followee = %s"""
    else:
        query = """INSERT INTO followers (follower, followee)
                   VALUES (%s, %s)"""

    c = db.cursor()
    c.execute(query, (kwargs['follower'], kwargs['followee']))
    db.commit()
    c.close()

    email = get_email_by_id(db, int(kwargs['follower']))
    return details(db, user=email)


def listFollowers(db, handler=get_info_by_id, **kwargs):
    required(['user'], kwargs)
    optional('limit', kwargs)
    optional('order', kwargs, 'desc')
    if 'order' not in kwargs:
        raise Exception("ill formatted request. Order not in ['desc', 'asc']")
    optional('since_id', kwargs)

    user_id = get_id_by_email(db, kwargs['user'])

    followers = []

    c = db.cursor()
    query = """SELECT followers.follower FROM followers
               INNER JOIN user ON followers.follower = user.id
               WHERE followers.followee = %s AND unfollowed = 0"""
    params = (user_id, )

    if kwargs['since_id'] is not None:
        query += """ AND followers.follower > %s"""
        params += kwargs['since_id']

    if kwargs['limit'] is not None:
        query += """ LIMIT %s"""
        params += kwargs['limit']

    query += """\nORDER BY user.name"""

    c.execute(query, params)
    data = c.fetchall()
    c.close()

    for row in data:
        info = handler(db, row['follower'])
        followers.append(info)

    return followers


def listFollowing(db, handler=get_info_by_id, **kwargs):
    required(['user'], kwargs)
    optional('limit', kwargs)
    optional('order', kwargs, 'desc')
    if 'order' not in kwargs:
        raise Exception("ill formatted request. Order not in ['desc', 'asc']")
    optional('since_id', kwargs)

    user_id = get_id_by_email(db, kwargs['user'])

    followees = []

    c = db.cursor()
    query = """SELECT followers.followee FROM followers
               INNER JOIN user ON followers.followee = user.id
               WHERE followers.follower = %s AND unfollowed = 0"""
    params = (user_id, )

    if kwargs['since_id'] is not None:
        query += """ AND followers.followee > %s"""
        params += kwargs['since_id']

    if kwargs['limit'] is not None:
        query += """ LIMIT %s"""
        params += kwargs['limit']

    query += """\nORDER BY user.name"""

    c.execute(query, params)
    data = c.fetchall()
    c.close()

    for row in data:
        info = handler(db, row['followee'])
        followees.append(info)

    return followees


def listPosts(db, **kwargs):
    pass


def unfollow(db, **kwargs):
    required(['follower', 'followee'], kwargs)

    c = db.cursor()
    c.execute("""UPDATE followers SET unfollowed=1
                 WHERE follower = %s AND followee = %s""",
              (kwargs['follower'], kwargs['followee']))
    db.commit()
    c.close()

    email = get_email_by_id(db, int(kwargs['follower']))
    return details(db, user=email)


def updateProfile(db, **kwargs):
    required(['about', 'user', 'name'], kwargs)

    c = db.cursor()
    c.execute("""UPDATE user
                 SET about = %s,
                     name = %s
                 WHERE email = %s""",
              (kwargs['about'], kwargs['name'], kwargs['user']))
    db.commit()
    c.close()

    return details(db, user=kwargs['user'])
