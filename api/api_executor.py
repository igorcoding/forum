import timeit
from api.util.DataService import DataService


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
        start = timeit.timeit()
        result = func(ds, **data)
        end = timeit.timeit()
        print "Elapsed time: " + str(end - start)

        response = response_good(result)
    except Exception as e:
        print str(e)
        response = response_error(str(e))
    ds.close_all()

    return response


def clear_db():
    ds = DataService()
    try:
        ds.truncate()
        res = "Cleared"
    except Exception as e:
        res = "Error"
    return res