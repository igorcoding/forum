def get_id_by_short_name(db, short_name):
    c = db.cursor()
    c.execute("""SELECT id FROM forum
               WHERE short_name = %s""", (short_name,))
    id = c.fetchone()['id']
    c.close()
    return id