
def response_good(response_info):
    return {
        'code': 0,
        'response': response_info
    }


def response_error(msg):
    return {
        'code': 1,
        'message': msg
    }


def parse_get(get):
    get_dict = {}
    for elem in get:
        cur = get
        get_dict[elem] = get[elem][0] if len(get[elem]) == 1 else get[elem]
    return get_dict