def get_id_by_email(db, email):
    c = db.cursor()
    c.execute("""SELECT id FROM user
               WHERE email = %s""", (email,))
    id = c.fetchone()['id']
    c.close()
    return id


def get_email_by_id(db, user_id):
    c = db.cursor()
    c.execute("""SELECT email FROM user
               WHERE id = %s""", (user_id,))
    email = c.fetchone()['email']
    c.close()
    return email


def get_info_by_id(db, user_id):
    from forumApi.api.user import details

    email = get_email_by_id(db, user_id)
    return details(db, user=email)


def get_subscriptions_by_user(db, email):
    user_id = get_id_by_email(db, email)

    c = db.cursor()
    c.execute("""SELECT thread_id FROM subscriptions
               WHERE user_id = %s""", (user_id,))

    c.close()
    return None