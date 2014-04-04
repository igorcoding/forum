import json


def required(param_list, args):
    for param in param_list:
        if type(param) != str:
            raise Exception("param must be a string value")
        if param not in args:
            raise Exception("%s is required." % (param,))


def semi_required(param_variations, args):
    atleast = False
    all = True
    for param in param_variations:
        arg = param in args
        atleast = atleast or arg
        all = all and arg

    if all:
        raise Exception("All variations cannot be in one request simultaneously")
    if not atleast:
        raise Exception("None of variations is in the arguments list")


def optional(param, args, default=None, possible_values=None):
    if param not in args:
        args[param] = default

    try:
        args[param] = json.loads(args[param], encoding='utf-8')
    except:
        args[param] = args[param]

    def check_arg(arg, values):
        if arg not in values:
            raise Exception("%s not in %s" % (arg, values))

    if type(args[param]) == list and type(possible_values) == list:
        for arg in args[param]:
            check_arg(arg, possible_values)

    if type(args[param]) != list and type(possible_values) == list:
        check_arg(args[param], possible_values)


def make_boolean(params, arr):
    for param in params:
        arr[param] = bool(arr[param])


def check_empty(res, message):
    if not res or len(res) == 0:
        raise Exception(message)