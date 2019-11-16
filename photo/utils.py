import sys
from functools import wraps
import traceback
import json
from django.http import QueryDict
from json.decoder import JSONDecodeError
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

default = {
    str:'',
    int:0,
    float:0.0,
    list:[],
    dict:{},
    tuple:(),
    bool:False,
    object:None
}

type_allowed = [str,int,float,list,dict,bool]

def copy(data,template):
    if type(template) == dict:
        for key in template.keys():
            pass

def parse(request, template, strict=False):
    data_dict = dict(QueryDict(request.body))
    if type(template) != dict:
        raise TypeError(f"Template with error type:[{type(template)}] (must be a [dict])")
    for key in template.keys():
        temp = template[key]
        if type(temp) == type and temp not in type_allowed:
            raise TypeError(f"Template type error: type[{temp}] not allowed")
        if key not in data_dict:
            if strict:
                raise KeyError(f"Template key:[{key}] does not in request data's keys")
            else:
                if temp in default.keys():
                    data_dict[key] = default[temp]
                else:
                    copy(data_dict[key], temp)
        else:
            data = data_dict[key]
            if type(data) == list:
                if temp == list:
                    pass
                elif type(temp) == list:
                    if temp[0] == dict:
                        pass
                    elif type(temp[0]) == dict:
                        pass # do recur
                    else:
                        t = temp[0]
                        for d in data:
                            if type(d) != t:
                                pass


def is_float(s):
    s = str(s)
    if s.count('.') == 1:  # 判断小数点个数
        sl = s.split('.')  # 按照小数点进行分割
        left = sl[0]  # 小数点前面的
        right = sl[1]  # 小数点后面的
        if left.startswith('-') and left.count('-') == 1 and right.isdigit():
            lleft = left.split('-')[1]  # 按照-分割，然后取负号后面的数字
            if lleft.isdigit():
                return True
        elif left.isdigit() and right.isdigit():
            # 判断是否为正小数
            return True
    return False

def type_decode(data):
    if type(data) == str:
        if data.isdigit() or (data.split('-')[-1]).isdigit():
            return int(data)
        elif is_float(data):
            return float(data)
        elif data == "true":
            return True
        elif data == "false":
            return False
        elif data == "null":
            return None
        else:
            try:
                d = json.loads(data)
                # print(d)
                return d
            except JSONDecodeError:
                return data
    else:
        return data



