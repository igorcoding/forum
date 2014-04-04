
def execute(entity, action, data):
    from api import forum, thread, user, post
    from api.util.DataService import DataService
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

    ds = DataService()
    try:
        result = func(ds, **data)
        response = response_good(result)
    except Exception as e:
        response = response_error(str(e))
    ds.close_all()

    return response
