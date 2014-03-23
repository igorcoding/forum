def response(code, response_info):
    return {
        'code': code,
        'response': response_info
    }


def response_good(response_info):
    return response(0, response_info)


def parse_get(get):
    get_dict = {}
    for elem in get:
        get_dict[elem] = get[elem][0] if len(get[elem]) == 1 else get[elem]
    return get_dict