import sys
from functools import wraps
import traceback
import json
from django.http import QueryDict
from io import BytesIO

from django.http.request import QueryDict


def request_serialize(request):
    if request.content_type == 'multipart/form-data':
        if hasattr(request, '_body'):
            # Use already read data
            data = BytesIO(request._body)
        else:
            data = request
        try:
            data_dict, files = request.parse_file_upload(request.META, data)
            return data_dict
        except:
            pass


def handle(error_occurred_move=None):
    def decorator(f):
        @wraps(f)
        def wrapper(arg, *args, **kwargs):
            try:
                return f(arg, *args, **kwargs)
            except Exception as e:
                exc_type, exc_instance, exc_traceback = sys.exc_info()
                formatted_traceback = ''.join(traceback.format_tb(exc_traceback))
                message = str('\n{0}\n{1}:\n{2}\n{3}'.format(
                    e,
                    formatted_traceback,
                    exc_type.__name__,
                    exc_instance
                ))#  .encode('utf-8').decode('unicode-escape')
                print(message)
                return error_occurred_move
        return wrapper
    return decorator


def corr(data, template):
    msg = 'correspond success'
    for key in data.keys():
        if key not in template:
            msg = f"data don't has key:[{key}]"
            return False, msg
        elif type(data[key]) == dict:
            correspond, msg = corr(data[key], template[key])
            if not correspond:
                return False, msg
        elif type(data[key]) == list:
            pass
        elif type(data[key]) != template[key]:
            msg = f"data's key:[{key}] with type:({type(data[key])}) don't match the type:({template[key]})"
            return False, msg
    return True, msg


temp1 = {
    'get':{
        'id': int
    }, 'post': {
        'name': str,
        'prop': list
    }
}
http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']


def check(request, template):
    data_dict = QueryDict(request.body)
    if type(template) != dict:
        raise TypeError(f"Template with error type:[{type(template)}] (must be a [dict])")
    for key in template.keys():
        temp = template[key]
        if key not in http_method_names or key.lower() not in http_method_names:
            raise KeyError(f"Template key:[{key}] does not in http method name")
        if type(temp) != dict:
            raise TypeError(f"SubTemplate with error type:[{type(temp)}] (must be a [dict])")
        if request.method == key.upper():
            correspond, msg = corr(data_dict, temp)
            if not correspond:
                raise AttributeError("Template match error:"+msg)
    return True

# def parse(raw):

