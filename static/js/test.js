let url,data,xhr;

url = "http://127.0.0.1:8000/test/";

data = JSON.stringify({
    'a': '123',
    'b': [1,2,3],
    'c': 'true',
    'd': '{"foo":"bar"}',
    'e':{
        'f':[1,2,3],
        'g':"uio"
    }
});



xhr = new XMLHttpRequest();

xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

xhr.open('post',url);
xhr.send(data);