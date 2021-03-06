from api.util.DataService import DataService


def execute(ds, entity, action, data):
    from api import forum, thread, user, post

    from api.util.response_helpers import response_good, response_error

    for key in data:
        if type(data[key]) == str:
            data[key] = data[key].replace("'", '"')

    entity = {
        "forum": forum,
        "user": user,
        "thread": thread,
        "post": post
    }[entity]

    #print data

    func = getattr(entity, action[:len(action)-1])

    # ds = DataService()
    try:
        result = func(ds, **data)
        response = response_good(result)
        # print ds.get_length()
    except Exception as e:
        response = response_error(str(e))
        # raise e
    # ds.close_all()
    # print response
    return response


def clear_db():
    ds = DataService()
    try:
        ds.truncate()
        res = "Cleared"
    except Exception as e:
        res = "Error"
    return res