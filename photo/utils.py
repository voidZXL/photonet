import sys, traceback,json


def handle(error_occurred_move=None):
    def decorator(f):
        def handle_problems(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                exc_type, exc_instance, exc_traceback = sys.exc_info()
                formatted_traceback = ''.join(traceback.format_tb(exc_traceback))
                message = '\n{0}\n{1}:\n{2}\n{3}'.format(
                    e,
                    formatted_traceback,
                    exc_type.__name__,
                    exc_instance
                )
                print(exc_type(message))
                return error_occurred_move
        return handle_problems
    return decorator


def check(request, gets, posts, files):
    GET = json.loads(request.GET.dict())
    POST = json.loads(request.POST.dict())
    FILE = json.loads(request.FILES.dict())
    pass