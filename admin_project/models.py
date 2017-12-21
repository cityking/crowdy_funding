from django.db import models
from config.tool import *
from crowdy_funding.project_content.models import ItemInfo
from config.myredis import MyRedis

# Create your models here.
class Role(models.Model):
    name = models.CharField(max_length=300, unique=True, verbose_name='角色名称')
    def __str__(self):
        return self.name
    
class Adminastrator(models.Model):
    password = models.CharField(max_length=32, null=True, verbose_name='密码')
    nick_name = models.CharField(max_length=300, unique=True, verbose_name='用户昵称')
#    role = models.ForeignKey(Role,models.SET_NULL,blank=True, null=True,verbose_name='角色')
    authority = models.CharField(max_length=32, default='item', verbose_name='权限')


    #default_consignee = models.


    class Meta:
        verbose_name = '管理员'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.nick_name
    def get_info(self):
        data = dict(nick_name=self.nick_name, authority=self.authority)
        return data
    def is_super(self):
        if self.authority == 'super':
            return True
        else:
            return False

    @classmethod
    def admin_login(cls, nick_name, password):
        adminastrator = cls.objects.filter(nick_name=nick_name)
        if adminastrator:
            adminastrator = adminastrator[0]
            password = make_password(password)
            if adminastrator.password and password == adminastrator.password:
                identity = make_admin_identity(nick_name, adminastrator)
                return identity
            else:
                return '0'
        else:
             return '1'

    @classmethod
    def add(cls, data):
        nick_name = data.get('nick_name')
        if nick_name:
            adminastrator = cls.objects.filter(nick_name=nick_name)
            if adminastrator:
                return '1'
        else:
             return '2'
        password = data.get('password')
        password_repeat = data.get('password_repeat')
        if password and password != password_repeat:
            return '0'
        if not password:
            return '3'
        password = make_password(password)
        if cls.objects.create(nick_name=nick_name, password=password):
            return nick_name
        else:
            return '4'

    @classmethod
    def get_adminastrator_by_identity(cls, identity):
        redis = MyRedis()
        key = 'identity' + identity
        nick_name = re.match('admin(.*)',redis.get(key)).group(1)
        if nick_name:
            adminastrator = cls.objects.get(nick_name=nick_name)
            if adminastrator:
                return adminastrator
            else:
                return None
        else:
             return None
    
class Announcement(models.Model):
    title = models.CharField(max_length=32, null=True, verbose_name='标题')
    content = models.CharField(max_length=300, unique=True, verbose_name='内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '公告'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
    def get_info(self):
        create_time = trans_to_localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')
        return dict(announce_id=self.id,
                announce_title=self.title,
                announce_content=self.content,
                create_time=create_time)

    def update(self, data):
        title = data.get('announce_title')
        if title:
            self.title = title
        content = data.get('announce_content')
        if content:
            self.content=content
        self.save()
        return self
    @classmethod
    def create(cls, data):
        title = data.get('announce_title')
        if not title:
            return '0'
        content = data.get('announce_content')
        if not content:
            return '1'
        announce = cls.objects.create(title=title, content=content)
        return announce

class Carousel(models.Model):
    item = models.ForeignKey(ItemInfo,models.SET_NULL,blank=True, null=True,verbose_name='轮播项目') 
    carousel_img = models.CharField(max_length=300, unique=True, verbose_name='轮播图片地址')

    class Meta:
        verbose_name = '轮播'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.item.item_name

    def get_info(self):
        return dict(carousel_id=self.id,
                item_id=self.item.id,
                item_name=self.item.item_name,
                carousel_img=self.carousel_img)

class Fee(models.Model):
    fee_type = models.CharField(max_length=20, verbose_name='手续费类型') #charge 充值 item 项目
    fee_money = models.FloatField(default=0, verbose_name='手续费用') 
    class Meta:
        verbose_name = '手续费'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.fee_type

   
