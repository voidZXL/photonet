from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views import View
from photo.models import Account, Album
from photo.utils import handle,request_serialize
import json
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required


test_temp = {
    'id': int,
    'name': str,
    'public': bool,
    'cases': [{
        'id': int,
        'name': str,
        'label': [str]
    }],
    'data': {
        'course': [int],
        'value': float,
        'sub': {
            'name': str,
            'desc': str
        }
    }
}

@csrf_exempt
def test(request):
    print(dict(request.DATA))
    print(request.META['CONTENT_TYPE'])
    return JsonResponse(request.POST.dict())


class AlbumView(View):
    data = {}
    data_temp = {
        'name': str,
        'desc': str,
        'public': bool,
        'photos': [{
            'name': str,
            'desc': str,
            'can_download': bool,
        }],
        'cover': int,
        'deletes': [int],
    }
    files_temp = {
        'file': list,
    }

    def check(self, request):
        pass

    def dispose(self):
        pass

    @handle()# (redirect('/'))
    def fetch(self, request):
        self.data = {
            'data': request.DATA,
            # 'photos': request.DATA['photos'],
            'files': request.FILES.getlist('file'),
        }

    @handle()# (redirect('/me'))
    def get(self, request, aid):
        # aid = request.GET.get('id')
        return JsonResponse(Album.get(aid).get_data())

    @handle(HttpResponse("0"))
    def post(self, request):
        self.fetch(request)
        self.data.update({
            'user': Account.get_user(request.session),
        })
        Album.create(**self.data)
        return HttpResponse('1')

    @handle(HttpResponse("0"))
    def put(self, request, aid):
        # put = request_serialize(request)
        print(request.DATA)
        # print(json.dumps(request.DATA, ensure_ascii=False))
        self.fetch(request)
        # Album.get(aid).modify(**self.data)
        return HttpResponse('1')

    @handle()
    def delete(self, request, aid):
        Album.get(aid).remove()
        return HttpResponse('1')

    @handle()# (HttpResponse("0"))
    def download(self, request, aid):
        return FileResponse(Album.get(aid).get_zip())


# def album(request):
#     if request.method == 'POST':
#         try:
#             user = Account.get_user(request.session)
#
#             aid = request.POST.get('id')
#             name = request.POST.get('name')
#             desc = request.POST.get('desc')
#             photos = request.FILES.getlist('file')
#             info = request.POST.get('info')
#
#             public = True if request.POST.get('type') == 'publish' else False
#             if aid == 0:
#                 Album.create(user, name, desc, public, photos, info)
#             else:
#                 deletes = request.POST.get('deletes')
#                 Album.get(aid).modify(name, desc, public, photos, deletes, info)
#             return HttpResponse('1')
#         except Exception as e:
#             print(e)
#             return HttpResponse('0')
#     if request.method == 'GET':
#         id = request.GET.get('id')
#         return JsonResponse(Album.get(id).get_data())


# @handle(redirect('/'))
def join(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        in_type = request.POST.get('type')

        if in_type == 'login':
            if Account.login(username, password):
                request.session['user'] = username
                return redirect('/me')
        elif in_type == 'signup':
            if Account.signup(username, password):
                request.session['user'] = username
                return redirect('/me')
    return redirect('/')


# @handle
def me(request):
    if 'user' in request.session:
        user = Account.get(request.session['user'])
        return render(request, 'me.html', user.get_data())
    return redirect('/')


def index(request):
    return render(request, 'index.html')



