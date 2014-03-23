def required(param_list, kwargs):
    for param in param_list:
        if type(param) != str:
            raise Exception("param must be a string value")
        if param not in kwargs:
            raise Exception("%s is required." % (param,))


def semi_required(param_variations, kwargs):
    atleast = False
    all = True
    for param in param_variations:
        arg = param in kwargs
        atleast = atleast or arg
        all = all and arg

    if all:
        raise Exception("All variations cannot be in one request simultaneously")
    if not atleast:
        raise Exception("None of variations is in the arguments list")


def optional(param, kwargs, default=None, possible_values=None):
    if param not in kwargs:
        kwargs[param] = default

    def check_arg(arg, values):
        if arg not in values:
            raise Exception("%s not in %s" % (arg, values))

    if type(kwargs[param]) == list and type(possible_values) == list:
        for arg in kwargs[param]:
            check_arg(arg, possible_values)

    if type(kwargs[param]) != list and type(possible_values) == list:
        check_arg(kwargs[param], possible_values)


def make_boolean(params, arr):
    for param in params:
        arr[param] = bool(arr[param])