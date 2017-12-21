# 用户
class User(BaseModel):
    authority = ManyToManyField(Authority, related_name='user')
    unionid = peewee.CharField(null=True, help_text='unionId')
    openid = peewee.CharField(max_length=64, help_text='用户openid')
    role = peewee.IntegerField(default=0)
    about_me = peewee.TextField(default='这个人很懒，什么都没有留下。', help_text='个性签名')
    avatar_url = peewee.CharField(max_length=300, null=True, help_text='用户头像')
    nick_name = peewee.CharField(max_length=300, null=True, help_text='用户昵称')
    join_date = peewee.DateTimeField(default=datetime.datetime.now(), help_text='加入时间')
    last_login = peewee.DateTimeField(default=datetime.datetime.now(), help_text='上次登录')
    real_name = peewee.CharField(max_length=8, null=True, help_text='真实姓名')
    mobile = peewee.CharField(max_length=32, null=True, help_text='手机号')
    sex = peewee.CharField(max_length=4, null=True, help_text='性别')
    age = peewee.IntegerField(default=0, null=True, help_text='年龄')
    id_card = peewee.CharField(max_length=32, null=True, help_text='身份证')
    address = peewee.CharField(max_length=64, null=True, help_text='地址')
    balance = peewee.IntegerField(default=0, help_text='钱包余额')
    state = peewee.IntegerField(default=0, help_text='0:开启；1：禁用')

    def ping(self):
        self.last_login = datetime.datetime.now()
        self.save()

    def get_avatar(self):
        if self.avatar_url.startswith('https://wx.qlogo.cn/mmopen'):
            return self.avatar_url
        else:
            return config.QINIU_BUCKET_NAME + self.avatar_url

    def to_json(self):
        return dict(user_id=self.id,
                    openid=self.openid,
                    avatar_url=self.get_avatar(),
                    nick_name=self.nick_name,
                    )

    def get_info(self):
        return dict(user_id=self.id,
                    openid=self.openid,
                    role=self.role,
                    about_me=self.about_me,
                    avatar_url=self.get_avatar(),
                    nick_name=self.nick_name,
                    last_login=self.last_login.strftime('%Y-%m-%d %H:%M:%S'),
                    balance=self.balance,
                    )
