
d = {
    'v1':1,
    'v2':2,
    'v3':3
}


def func(v2,v3,v1):
    print(v1,v2,v3)

def fun2(dic):
    print(dic)

func(**d)
fun2(d)

# 参数顺序无关紧要，字典用**kwargs的方法可以将键名匹配参数传入

# json相关：
# c= '{"a": true, "b": 2}'
# d=json.loads(c)
# d
# {'a': True, 'b': 2}
# d['a']
# True
# type(d['a'])
# <class 'bool'>
# c= '{"a": True, "b": 2}'
# d=json.loads(c)
# json.decoder.JSONDecodeError: Expecting value: