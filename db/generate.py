import datetime
import json
import requests
from random_words import *
import random

users = []
forums = []
threads = []
posts = []
followers = []
subscriptions = []

url_prefix = "http://localhost/igor/"
echo = False


def check_in_arr(array, obj_key, value):
    if value is None:
        return True
    for obj in array:
        if obj_key in obj and obj[obj_key] == value:
            return True
    return False


def get_rand_int(max_value=99999):
    return random.randint(0, max_value)


def trim_title(title):
    return title.lower().replace(' ', '')


def get_random_datetime():
    return datetime.datetime(random.randint(2005, 2014),
                             random.randint(1, 12),
                             random.randint(1, 28),
                             random.randint(0, 23),
                             random.randint(0, 59),
                             random.randint(0, 59),
                             random.randint(0, 1000)).strftime("%Y-%m-%d %H:%M:%S")


def generate_users(count):
    emails = RandomEmails()
    names = RandomNicknames()
    texts = LoremIpsum()

    def gen_unique_name():
        rand_name = None
        while check_in_arr(users, 'user', rand_name):
            rand_name = names.random_nick(gender='u') + str(get_rand_int())
        return rand_name

    def gen_unique_email():
        rand_email = None
        while check_in_arr(users, 'user', rand_email):
            rand_email = emails.randomMail()
        return rand_email

    for i in range(0, count):
        name = gen_unique_name()
        user = {
            'username': name,
            'name': name,
            'email': gen_unique_email(),
            'about': texts.get_sentence(),
            'isAnonymous': bool(random.randint(0, 1))
        }
        users.append(user)


def generate_forums(count):
    rw = RandomWords()

    def gen_unique_forum():
        rand_forum = None
        while check_in_arr(forums, 'name', rand_forum):
            rand_forum = " ".join(rw.random_words(count=4)).capitalize()
        return rand_forum

    for i in range(0, count):
        forum = {
            'name': gen_unique_forum(),
            'short_name': None,
            'user': random.choice(users)['email']
        }
        forum['short_name'] = trim_title(forum['name'])
        forums.append(forum)


def generate_threads(count):
    rw = RandomWords()

    def gen_unique_title():
        title = None
        while check_in_arr(threads, 'title', title):
            title = " ".join(rw.random_words(count=5)).capitalize()
        return title

    for i in range(0, count):
        thread = {
            'forum': random.choice(forums)['short_name'],
            'title': gen_unique_title(),
            'slug': None,
            'isClosed': bool(random.randint(0, 1)),
            'isDeleted': bool(random.randint(0, 1)),
            'user': random.choice(users)['email'],
            'date': get_random_datetime(),
            'message': LoremIpsum().get_sentences(2),
            'id': i+1,
        }
        thread['slug'] = trim_title(thread['title'])
        threads.append(thread)


def generate_posts(count):
    rand_thread = random.choice(threads)

    for i in range(0, count):
        post = {
            'forum': rand_thread['forum'],
            'thread': rand_thread['id'],
            'isApproved': bool(random.randint(0, 1)),
            'isHighlighted': bool(random.randint(0, 1)),
            'isEdited': bool(random.randint(0, 1)),
            'isSpam': bool(random.randint(0, 1)),
            'isDeleted': bool(random.randint(0, 1)),
            'user': random.choice(users)['email'],
            'date': get_random_datetime(),
            'message': LoremIpsum().get_sentences(2),
            'parent': random.choice([None] + range(1, i)),
            'id': i+1,
        }
        posts.append(post)


def generate_followers(count):
    for i in range(0, count):
        f = {
            'follower': random.choice(users)['email'],
            'followee': None,
        }

        while f['followee'] is None or f['followee'] == f['follower']:
            f['followee'] = random.choice(users)['email']

        followers.append(f)


def generate_subscriptions(count):
    for i in range(0, count):
        s = {
            'user': random.choice(users)['email'],
            'thread': random.choice(threads)['id']
        }

        subscriptions.append(s)


def send_users():
    for user in users:
        r = requests.post(url_prefix + 'user/create/', data=json.dumps(user))
        if echo:
            print r.text


def send_forums():
    for forum in forums:
        r = requests.post(url_prefix + 'forum/create/', data=json.dumps(forum))
        if echo:
            print r.text


def send_threads():
    for thread in threads:
        r = requests.post(url_prefix + 'thread/create/', data=json.dumps(thread))
        if echo:
            print r.text


def send_posts():
    for post in posts:
        r = requests.post(url_prefix + 'post/create/', data=json.dumps(post))
        if echo:
            print r.text


def send_followers():
    for f in followers:
        r = requests.post(url_prefix + 'user/follow/', data=json.dumps(f))
        if echo:
            print r.text


def send_subscriptions():
    for s in subscriptions:
        r = requests.post(url_prefix + 'thread/subscribe/', data=json.dumps(s))
        if echo:
            print r.text


def main():
    users_count = 10
    forums_count = 30
    threads_count = 80
    posts_count = 200
    followers_count = 7
    subscriptions_count = 300

    generate_users(users_count)
    generate_forums(forums_count)
    generate_threads(threads_count)
    generate_posts(posts_count)
    generate_followers(followers_count)
    generate_subscriptions(subscriptions_count)

    send_users()
    send_forums()
    send_threads()
    send_posts()
    send_followers()
    send_subscriptions()


if __name__ == "__main__":
    main()
