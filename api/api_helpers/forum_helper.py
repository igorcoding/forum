def get_id_by_short_name(ds, short_name):
    db = ds.get_db()
    c = db.cursor()
    c.execute("""SELECT id FROM forum
               WHERE short_name = %s""", (short_name,))
    id = c.fetchone()['id']
    c.close()
    ds.close_last()
    return id