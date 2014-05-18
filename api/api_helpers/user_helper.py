def get_id_by_email(ds, email):
    conn = ds.get_db()
    db = conn['conn']
    c = db.cursor()
    c.execute("""SELECT id FROM user
               WHERE email = %s""", (email,))
    id = c.fetchone()['id']
    c.close()
    ds.close(conn['id'])
    return id


def get_email_by_id(ds, user_id):
    conn = ds.get_db()
    db = conn['conn']
    c = db.cursor()
    c.execute("""SELECT email FROM user
               WHERE id = %s""", (user_id,))
    email = c.fetchone()['email']
    c.close()
    ds.close(conn['id'])
    return email


def echo_email(ds, email):
    return email


def get_info_by_id(ds, user_id):
    from api.user import details

    email = get_email_by_id(ds, user_id)
    return details(ds, user=email)


def get_info_by_email(ds, email):
    from api.user import details
    return details(ds, user=email)


def get_subscriptions_by_user(ds, email):
    user_id = get_id_by_email(ds, email)

    conn = ds.get_db()
    db = conn['conn']
    c = db.cursor()
    c.execute("""SELECT thread_id FROM subscriptions
               WHERE user_id = %s""", (user_id,))

    c.close()
    ds.close(conn['id'])
    return None