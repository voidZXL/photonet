from django.db import models
import uuid, os
import zipfile
from PIL import Image
from photonet.settings import IMAGE_ROOT, BASE_DIR


def zip_files(path, name):
    zip_path = os.path.join(BASE_DIR, 'zip', name)
    if os.path.exists(zip_path):
        return open(zip_path, 'r')
    zip_file = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)
    for f in os.listdir(path):
        abs_path = os.path.join(path, f)
        rel_path = abs_path[len(os.getcwd())+1:]
        zip_file.write(rel_path)
    return zipfile


class Account(models.Model):
    username = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    portrait_name = models.CharField(max_length=42, default="")


    @classmethod
    def get(cls, urn):
        query = cls.objects.filter(username=urn)
        return query[0] if query else None

    @classmethod
    def login(cls, urn, pwd):
        return cls.objects.filter(username=urn, password=pwd)

    @classmethod
    def signup(cls, urn, pwd):
        if cls.get(urn):
            return False
        return cls.objects.create(username=urn, password=pwd)



    @classmethod
    def get_user(cls, session):
        if 'user' not in session:
            return None
        return cls.get(session['user'])

    def get_data(self):
        return {
            'id': self.id,
            'username':self.username,
            'name': self.name,
            'portrait_name': self.portrait_name,
            'albums': self.get_albums()
        }

    def get_albums(self):
        result = []
        for a in self.album_set.all():
            result.append(a.get_data())
        return result



    class Meta:
        db_table = 'account'


class Content(models.Model):
    creator = models.ForeignKey('Account', on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    description = models.TextField()
    create_date = models.DateField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True


class Photo(Content):
    album = models.ForeignKey('Album', on_delete=models.CASCADE)
    image_name = models.CharField(max_length=42)
    can_download = models.BooleanField(default=False)

    PREVIEW_SIZE = 600
    THUMB_SIZE = 100

    @classmethod
    def store(cls, file):
        name = str(uuid.uuid4()) + "." + file.name.split(".")[-1]
        raw_path = os.path.join(IMAGE_ROOT, 'raw', name)
        preview_path = os.path.join(IMAGE_ROOT, 'preview', name)
        thumb_path = os.path.join(IMAGE_ROOT, 'thumb', name)

        img = Image.open(file)
        w, h = img.size
        if w > h:
            preview_w = cls.PREVIEW_SIZE
            preview_h = h * preview_w / w
            thumb_h = cls.THUMB_SIZE
            thumb_w = w * thumb_h / h
        else:
            preview_h = cls.PREVIEW_SIZE
            preview_w = w * preview_h / h
            thumb_w = cls.THUMB_SIZE
            thumb_h = h * thumb_w / w

        preview_img = img.resize((int(preview_w), int(preview_h)), Image.ANTIALIAS)
        thumb_img = img.resize((int(thumb_w), int(thumb_h)), Image.ANTIALIAS)
        preview_img.save(preview_path)
        thumb_img.save(thumb_path)
        f = open(raw_path, 'wb')
        for chunk in file.chunks():
            f.write(chunk)
        f.close()
        return name

    @classmethod
    def remove(cls, name):
        raw_path = os.path.join(IMAGE_ROOT, 'raw', name)
        preview_path = os.path.join(IMAGE_ROOT, 'preview', name)
        thumb_path = os.path.join(IMAGE_ROOT, 'thumb', name)
        size = os.path.getsize(raw_path)
        try:
            cls.objects.get(image_name=name).delete()
            os.remove(raw_path)
            os.remove(preview_path)
            os.remove(thumb_path)
            return size
        except Exception as e:
            return 0


    class Meta:
        db_table = 'photo'


def process_size(size, depth=0):
    UNIT = ['B', 'K', 'M', 'G', 'T']
    if 1 < size < 1000:
        return str(size) + UNIT[depth]
    return process_size(int(size/1024), depth+1)


class Album(Content):
    public = models.BooleanField(default=False)
    cover = models.ForeignKey('Photo', related_name='covered_album', on_delete=models.CASCADE)
    edit_date = models.DateField(auto_now=True)
    total_size = models.PositiveIntegerField()

    @classmethod
    def get(cls, _id):
        query = cls.objects.filter(id=_id)
        return query[0] if query else None

    def get_data(self):
        return{
            'id': self.id,
            'name': self.name,
            'desc': self.description,
            'public': self.public,
            'photos': self.get_photos(),
            'size': process_size(self.total_size),
            'cover': self.photo_set.last().image_name,
            'date': self.create_date.strftime("%Y-%m-%d"),
            'likes': self.likes
        }

    def get_zip(self):
        name = self.name+'_'+str(self.id)+'.zip'
        zip_path = os.path.join(BASE_DIR, 'zip', name)
        if os.path.exists(zip_path):
            return open(zip_path, 'rb')
        zip_file = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)
        for p in self.photo_set.all():
            path = os.path.join(IMAGE_ROOT, 'raw', p.image_name)
            file_name = p.name + '.' + p.image_name.split(".")[-1]
            zip_file.write(path, file_name)
        return open(zip_path, 'rb')

    def get_photos(self):
        result = []
        for p in self.photo_set.all():
            result.append({
                'id': self.id,
                'name': p.name,
                'image': p.image_name,
                'date': self.create_date.strftime("%Y-%m-%d"),
                'likes': p.likes,
            })
        return result

    def add_photos(self, files, info):
        size = 0
        for i, file in enumerate(files):
            size += file.size()
            photo = Photo.objects.create(creator=self.creator,
                                         name=info[i]['name'],
                                         descripton=info[i]['desc'],
                                         image_name=Photo.store(file),
                                         album=self)
            if info['is_cover']:
                self.cover = photo
        return size

    def modify(self, album, files):
        self.name = album['name']
        self.desc = album['desc']
        self.public = album['public']
        self.cover_id = album['cover'] or 0
        size = self.add_photos(files, album['photos'])
        self.total_size += size
        for d in album['deletes']:
            size += Photo.remove(d)
        self.total_size -= size
        self.save()

    def remove(self):
        for f in self.photo_set.all():
            f.remove(f.image_name)
        self.delete()

    @classmethod
    def create(cls, user, album, files):
        album = cls.objects.create(creator=user, name=album['name'],
                                   public=album['public'], description=album['desc'])
        album.total_size = album.add_photos(files, album['photos'])
        album.save()
        return album

    class Meta:
        db_table = 'album'

# Create your models here.
