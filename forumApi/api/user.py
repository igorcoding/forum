from forumApi.api.helpers.user_helper import *
from forumApi.util.helpers import response_good


def create(db, **kwargs):
    pass


def details(db, output='resp', **kwargs):
    if 'user' not in kwargs:
        raise Exception("user email is required.")
    if output not in ['raw', 'resp']:
        raise Exception("if output not in ['raw', 'resp'].")

    c = db.cursor()
    c.execute("""SELECT * FROM user
               WHERE email = %s""", (kwargs['user'],))
    user_data = c.fetchone()
    c.close()
    user_data['isAnonymous'] = bool(user_data['isAnonymous'])

    user_data['followers'] = list_followers(db, handler=get_email_by_id, user=kwargs['user'])
    user_data['followees'] = list_following(db, handler=get_email_by_id, user=kwargs['user'])

    # getting subscriptions
    c = db.cursor()
    subscriptions = []
    c.execute("""SELECT thread_id FROM subscriptions
                 WHERE user_id = %s""", (user_data['id'],))
    for s in c:
        subscriptions.append(s['thread_id'])
    c.close()

    user_data['subscriptions'] = subscriptions

    if output == 'resp':
        return response_good(user_data)
    else:
        return user_data


def follow(db, **kwargs):
    pass


def list_followers(db, handler=get_info_by_id, **kwargs):
    if 'user' not in kwargs:
        raise Exception("user email is required.")
    if 'limit' not in kwargs:
        kwargs['limit'] = None
    if 'order' not in kwargs:
        kwargs['order'] = 'desc'
    if 'order' not in kwargs:
        raise Exception("ill formatted request. Order not in ['desc', 'asc']")
    if 'since_id' not in kwargs:
        kwargs['since_id'] = None

    user_id = get_id_by_email(db, kwargs['user'])

    followers = []

    c = db.cursor()
    query = """SELECT followers.follower FROM followers
               INNER JOIN user ON followers.follower = user.id
               WHERE followers.followee = %s"""
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


def list_following(db, handler=get_info_by_id, **kwargs):
    if 'user' not in kwargs:
        raise Exception("user email is required.")
    if 'limit' not in kwargs:
        kwargs['limit'] = None
    if 'order' not in kwargs:
        kwargs['order'] = 'desc'
    if 'order' not in kwargs:
        raise Exception("ill formatted request. Order not in ['desc', 'asc']")
    if 'since_id' not in kwargs:
        kwargs['since_id'] = None

    user_id = get_id_by_email(db, kwargs['user'])

    followees = []

    c = db.cursor()
    query = """SELECT followers.followee FROM followers
               WHERE followers.follower = %s"""
    params = (user_id, )

    if kwargs['since_id'] is not None:
        query += """ AND followers.followee > %s"""
        params += kwargs['since_id']

    if kwargs['limit'] is not None:
        query += """ LIMIT %s"""
        params += kwargs['limit']

    c.execute(query, params)
    data = c.fetchall()
    c.close()

    for row in data:
        info = handler(db, row['followee'])
        followees.append(info)

    return followees


def list_posts(db, **kwargs):
    pass


def unfollow(db, **kwargs):
    pass


def update_profile(db, **kwargs):
    pass
