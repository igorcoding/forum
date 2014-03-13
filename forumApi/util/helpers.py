def response(code, response_info):
    return {
        'code': code,
        'response': response_info
    }


def response_good(response_info):
    return response(0, response_info)
