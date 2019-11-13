import requests

url = "http://127.0.0.1:8000/test/"

data = {
    'a': '123',
    'b': [1,2,3],
    'c': 'true',
    'd': '{"foo":"bar"}',
    'e':{
        'f':[1,2,3],
        'g':"uio"
    }
}

r = requests.request("post", url, data=data)
print(r.text)
