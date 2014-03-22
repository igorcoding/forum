def required(param_list, kwargs):
    for param in param_list:
        if type(param) != str:
            raise Exception("param must be a string value")
        if param not in kwargs:
            raise Exception("%s is required." % (param,))


def optional(param, kwargs, default=None):
    if param not in kwargs:
        kwargs[param] = default