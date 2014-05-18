import datetime
import json
import requests
from random_words import *
import random
import MySQLdb
import MySQLdb.cursors

users = []
forums = []
threads = []
posts = []
followers = []
subscriptions = []

users_count = 10000
forums_count = 300
threads_count = 8000
posts_count = 1000000
followers_count = 400
subscriptions_count = 300

url_prefix = "http://localhost/db/api/"
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

def clear():
	print "Clearing up... "
	r = requests.post(url_prefix + 'clear/')
	if echo:
		print r.text

def send(url_suffix, data):
	r = requests.post(url_prefix + url_suffix, data=json.dumps(data))
	if echo:
		print r.text




db = MySQLdb.connect(host='localhost',
					 port=3306,
					 db='forum_db',
					 user='forum_db_user',
					 passwd='forum_db_user',
					 cursorclass=MySQLdb.cursors.SSDictCursor,
					 charset='utf8')


def insert_user(args):
	c = db.cursor()
	try:
		c.execute(u"""INSERT INTO user (id, username, name, email, about, isAnonymous, password)
					 VALUES (%s, %s, %s, %s, %s, %s, %s)""",
				  (args['id'], args['username'], args['name'], args['email'],
				   args['about'], int(args['isAnonymous']), '123456'))
		db.commit()
	except Exception as e:
		db.rollback()
		raise e
	finally:
		c.close()

def insert_forum(args):
	c = db.cursor()
	try:
		c.execute(u"""INSERT INTO forum (id, name, short_name, user, user_id)
					 VALUES (%s, %s, %s, %s, %s)""",
				  (args['id'], args['name'], args['short_name'], args['user'], args['user_id']))
		db.commit()
	except Exception as e:
		db.rollback()
		raise e
	finally:
		c.close()

def insert_thread(args):
	c = db.cursor()
	try:
		c.execute(u"""INSERT INTO thread (id, forum, forum_id, title, isClosed, user, user_id, date, message, slug, isDeleted)
					 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
				  (args['id'], args['forum'], args['forum_id'], args['title'], int(args['isClosed']), args['user'],
				   args['user_id'], args['date'], args['message'], args['slug'], int(args['isDeleted'])))
		thread_id = db.insert_id()
		db.commit()
	except Exception as e:
		db.rollback()
		raise e
	finally:
		c.close()

def insert_post(args):
	c = db.cursor()
	try:
		c.execute(u"""INSERT INTO post (id, date, thread_id, message, user, user_id, forum, parent,
									   isApproved, isHighlighted, isEdited, isSpam, isDeleted)
					 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
				  (args['id'], args['date'], args['thread'], args['message'], args['user'], args['user_id'], args['forum'], args['parent'],
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



def insert(table, data):
	inserter = {
		'user': insert_user,
		'forum': insert_forum,
		'thread': insert_thread,
		'post': insert_post
	}[table]

	inserter(data)


def generate_users(count):
	users_temp = []

	print "Generating users"
	emails = RandomEmails()
	names = RandomNicknames()
	texts = LoremIpsum()

	def gen_unique_name():
		rand_name = None
		while check_in_arr(users_temp, 'user', rand_name):
			rand_name = names.random_nick(gender='u') + str(get_rand_int())
		return rand_name

	def gen_unique_email():
		rand_email = None
		while check_in_arr(users_temp, 'email', rand_email):
			rand_email = emails.randomMail() + str(get_rand_int())
		return rand_email

	for i in range(0, count):
		if i % 100 == 0:
			print "%d users generated" % i

		name = gen_unique_name()
		user = {
			'id': i + 1,
			'username': name,
			'name': name,
			'email': gen_unique_email(),
			'about': texts.get_sentence(),
			'isAnonymous': bool(random.randint(0, 1))
		}
		# send('user/create/', user)
		insert('user', user)
		users_temp.append(user)
		users.append({
			'email': user['email'],
			'id': user['id']
		})
	users_temp = []


def generate_forums(count):
	forums_temp = []
	print "Generating forums"

	rw = RandomWords()

	def gen_unique_forum():
		rand_forum = None
		while check_in_arr(forums_temp, 'name', rand_forum):
			rand_forum = " ".join(rw.random_words(count=4)).capitalize()
		return rand_forum

	for i in range(0, count):
		if i % 100 == 0:
			print "%d forums generated" % i

		rand_user = random.choice(users)
		forum = {
			'id': i + 1,
			'name': gen_unique_forum(),
			'short_name': None,
			'user': rand_user['email'],
			'user_id': rand_user['id']
		}
		forum['short_name'] = trim_title(forum['name'])

		# send('forum/create/', forum)
		insert('forum', forum)
		forums_temp.append(forum)
		forums.append({
			'short_name': forum['short_name'],
			'id': forum['id']
		})
	forums_temp = []


def generate_threads(count):
	threads_temp = []
	print "Generating threads"
	rw = RandomWords()

	def gen_unique_title():
		title = None
		while check_in_arr(threads_temp, 'title', title):
			title = " ".join(rw.random_words(count=5)).capitalize()
		return title

	for i in range(0, count):
		if i % 100 == 0:
			print "%d threads generated" % i

		rand_forum = random.choice(forums)
		rand_user = random.choice(users)
		thread = {
			'forum': rand_forum['short_name'],
			'forum_id': rand_forum['id'],
			'title': gen_unique_title(),
			'slug': None,
			'isClosed': bool(random.randint(0, 1)),
			'isDeleted': bool(random.randint(0, 1)),
			'user': rand_user['email'],
			'user_id': rand_user['id'],
			'date': get_random_datetime(),
			'message': LoremIpsum().get_sentences(2),
			'id': i+1,
		}
		thread['slug'] = trim_title(thread['title'])

		# send('thread/create/', thread)
		insert('thread', thread)
		threads_temp.append(thread)
		threads.append(thread['id'])
	threads_temp = []


def generate_posts(count):
	print "Generating posts"
	for i in range(0, count):
		if i % 100 == 0:
			print "%d posts generated" % i

		rand_thread = random.choice(threads)

		rand_forum = random.choice(forums)
		rand_user = random.choice(users)
		post = {
			'forum': rand_forum['short_name'],
			'forum_id': rand_forum['id'],
			'thread': random.choice(threads),
			'isApproved': bool(random.randint(0, 1)),
			'isHighlighted': bool(random.randint(0, 1)),
			'isEdited': bool(random.randint(0, 1)),
			'isSpam': bool(random.randint(0, 1)),
			'isDeleted': bool(random.randint(0, 1)),
			'user': rand_user['email'],
			'user_id': rand_user['id'],
			'date': get_random_datetime(),
			'message': LoremIpsum().get_sentences(2),
			'parent': random.choice([None] + range(1, i)),
			'id': i+1,
		}
		insert('post', post)
		# send('post/create/', post)
		# posts_temp.append(post)
		# posts.append(id)


def generate_followers(count):
	print "Generating followers"

	for i in range(0, count):
		if i % 100 == 0:
			print "%d followers generated" % i

		f = {
			'follower': random.choice(users)['email'],
			'followee': None,
		}

		while f['followee'] is None or f['followee'] == f['follower']:
			f['followee'] = random.choice(users)['email']

		send('user/follow/', f)
		# followers.append(f)


def generate_subscriptions(count):
	print "Generating subscriptions"

	for i in range(0, count):
		if i % 100 == 0:
			print "%d subscribtions generated" % i

		s = {
			'user': random.choice(users)['email'],
			'thread': random.choice(threads)
		}

		send('thread/subscribe/', s)

		# subscriptions.append(s)


def main():
	clear()
	generate_users(users_count)
	generate_forums(forums_count)
	generate_threads(threads_count)
	generate_followers(followers_count)
	generate_subscriptions(subscriptions_count)
	generate_posts(posts_count)


if __name__ == "__main__":
	main()
