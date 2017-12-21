from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login, logout, authenticate
from config.myredis import MyRedis
from config.tool import make_password, make_identity, trans_to_localtime
import datetime
import urllib
import requests
import json

# Create your models here.

class Bank(models.Model):
    name = models.CharField(max_length=20, verbose_name='银行名称')
    log = models.CharField(max_length=100, null=True, blank=True, verbose_name='标志')

    class meta:
        verbose_name = '银行信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    @classmethod
    def get_list(cls):
        banks = Bank.objects.all()
        banks = [dict(bank_id=bank.id,bank_name=bank.name) for bank in banks]
        return banks

class BankCardInfo(models.Model):
    #bank = models.CharField(max_length=50, verbose_name='银行')
    bank = models.ForeignKey(Bank,models.SET_NULL,blank=True, null=True,verbose_name='银行')
    card_no = models.CharField(max_length=19, verbose_name='卡号')
    name = models.CharField(max_length=20, verbose_name='姓名')
    id_no = models.CharField(max_length=32, verbose_name='身份证号')
    phone = models.CharField(max_length=32, verbose_name='手机号码')
    
    class meta:
        verbose_name = '银行卡信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_info(self):
        return dict(bankcardinfo_id=self.id,
                bank_name=self.bank.name,
                bank_log = self.bank.log,
                card_no=self.card_no,
                name=self.name,
                id_no=self.id_no,
                phone=self.phone)
    @classmethod
    def create(cls, data):
        bank = data.get('bank')
        card_no = data.get('card_no')
        name = data.get('name')
        id_no = data.get('id_no')
        phone = data.get('phone')
        bankcard = cls.objects.create(bank=bank,
                card_no=card_no,
                name=name,
                id_no=id_no,
                phone=phone)
        return bankcard


 

SEX_CHOICES = (
    ('0', '男'),
    ('1', '女'),
)
certification_choices = (
       ('0','未认证'),
       ('1', '已认证'),
        )
class MyUser(models.Model):
    unionid = models.CharField(max_length=200, null=True, verbose_name='unionId')
    openid = models.CharField(max_length=64, verbose_name='用户openid')
    role = models.IntegerField(default=0)
    password = models.CharField(max_length=32, null=True, verbose_name='密码')
    about_me = models.TextField(default='这个人很懒，什么都没有留下。', verbose_name='个性签名')
    avatar_url = models.CharField(max_length=300, null=True, verbose_name='用户头像')
    nick_name = models.CharField(max_length=300, null=True, verbose_name='用户昵称')
    join_date = models.DateTimeField(default=datetime.datetime.now(), verbose_name='加入时间')
    last_login = models.DateTimeField(default=datetime.datetime.now(), verbose_name='上次登录')
    real_name = models.CharField(max_length=8, null=True, help_text='真实姓名')
    mobile = models.CharField(max_length=32, null=True, unique=True, verbose_name='手机号')
    sex = models.CharField(max_length=4, null=True, verbose_name='性别')
    age = models.IntegerField(default=0, null=True, verbose_name='年龄')
    id_card = models.CharField(max_length=32, null=True, verbose_name='身份证')
    address = models.CharField(max_length=64, null=True, verbose_name='地址')
    balance = models.FloatField(default=0, verbose_name='钱包余额')
    score = models.IntegerField(default=0, verbose_name='积分')
    day_score = models.IntegerField(default=0, verbose_name='日积分')
    week_score = models.IntegerField(default=0, verbose_name='周积分')
    month_score = models.IntegerField(default=0, verbose_name='月积分')
    state = models.IntegerField(default=0, verbose_name='0:开启；1：禁用')
    certification = models.CharField(max_length=2, choices=certification_choices, default='0', verbose_name='实名认证') #0未认证 1已认证
    banks = models.ManyToManyField(BankCardInfo, verbose_name='银行卡')

    #default_consignee = models.


    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.nick_name

    def get_bref(self):
        nick_name = self.nick_name
        mobile = self.mobile
        real_name = self.real_name
        create_time = self.join_date
        create_time = trans_to_localtime(create_time).strftime('%Y-%m-%d %H:%M:%S')
        state = self.state
        user_id = self.id
        return dict(user_id=user_id,
                nick_name=nick_name,
                mobile=mobile,
                real_name=real_name,
                create_time=create_time,
                state=state)



    def get_info(self):
        avatar_url = self.avatar_url
        nick_name = self.nick_name
        about_me = self.about_me
        certification = self.certification
        consignee = UserConsignee.objects.filter(user=self).filter(consignee_default='1')
        if consignee:
            address = consignee[0].consignee_region
        else:
            address = 'none'
        info = dict(avatar_url=avatar_url,
                nick_name=nick_name,
                about_me=about_me,
                certification=certification,
                address=self.address)
        return info

    def get_score_info(self, rank_type):
        avatar_url = self.avatar_url
        nick_name = self.nick_name
        about_me = self.about_me
        user_id = self.id
        if rank_type == 'week':
            score = self.week_score
        elif rank_type == 'month':
            score = self.month_score
        else:
            score = self.day_score

        info = dict(avatar_url=avatar_url,
                nick_name=nick_name,
                about_me=about_me,
                score=score
                )
        return info
           

    def add_score(self, score):
        self.score += score
        self.day_score += score
        self.week_score += score
        self.month_score += score


    def get_rank(self, rank_type):
        rank_count = 100
        if rank_type == 'week':
            ranks = MyUser.objects.filter(week_score__gt=0).order_by('-week_score')
        elif rank_type == 'month':
            ranks = MyUser.objects.filter(month_score__gt=0).order_by('-month_score')
        else:
            ranks = MyUser.objects.filter(day_score__gt=0).order_by('-day_score')
        users = [user for user in ranks]
        rank_list = [user.get_score_info(rank_type) for user in ranks]
        if not rank_list:
            return 'none'
        rank = 1
        for info in rank_list:
            info['rank'] = rank
            rank += 1
        if len(rank_list) > rank_count:
            ranks = rank_list[:rank_count]
        else:
            ranks = rank_list


        if self in users:
            index = users.index(self)
            rank = index+1
            if len(users) > rank_count and self not in users[:rank_count]:
                rank_score = ranks[-1]['score'] - ranks[index]['score']
            else:
                rank_score = 0
        else:
            rank = 0
            rank_score = ranks[-1]['score']
        user_info = self.get_score_info(rank_type)
        user_info.update(dict(rank=rank, rank_score=rank_score))
        data = {'user_info':user_info, 'ranks':ranks}
        return data
    def get_user_item(self):
        item = self.initiator_user_set.all()[0]
        return item.get_item_dict()
    
    def __str__(self):
        return self.nick_name


    @classmethod
    def get_user_by_identity(cls, identity):
        redis = MyRedis()
        key = 'identity' + identity
        user_id = redis.get(key) 
        if user_id:
            user = cls.objects.get(id=user_id)
            if user:
                return user
            else:
                return None
        else:
             return None

    @classmethod
    def create_weixin_login(cls, data):
        address = "%s %s %s" % (data['country'], data['province'], data['city'])
        if data['sex'] == '1':
            sex='男'
        else:
            sex='女'
        user = cls.objects.create(sex=sex,
                address=address,
                nick_name=data['nickname'],
                avatar_url=data['headimgurl'],
                openid=data['openid'],
                unionid=data['unionid'],
                )
        user.save()
        return user
    @classmethod
    def create_moblie_login(cls, mobile, password):
        if mobile:
            user = cls.objects.filter(mobile=mobile)
        else:
            return '1'
        if user:
            user = user[0]
            password = make_password(password)
            if user.password and password == user.password:
                identity = make_identity(mobile, user)
                return identity
            else:
                return '0'
        else:
             return '1'
    def get_banks_list(self):
        banks = self.banks.all()
        banks = [bank.get_info() for bank in banks]
        return banks

class UserConsignee(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE,verbose_name='用户')
    consignee_name = models.CharField(max_length=20, null=True, blank=True, verbose_name='收货人姓名')
    consignee_phone = models.CharField(max_length=11, null=True, blank=True, verbose_name='收货人电话')
    consignee_region = models.CharField(max_length=50, null=True, blank=True, verbose_name='地区信息')
    consignee_address = models.CharField(max_length=50, null=True, blank=True, verbose_name='收货人地址')
    consignee_default = models.CharField(max_length=2, default='0', verbose_name='默认')
    def __str__(self):
        return self.consignee_name
    class Meta:
        verbose_name = '收获地址'
        verbose_name_plural = verbose_name

    @classmethod
    def create(cls, data):
        user = data['user']
        consignee_name = data['consignee_name']
        consignee_phone = data['consignee_phone']
        consignee_address = data['consignee_address']
        consignee_region = data['consignee_region']
        consignees = cls.objects.filter(user=user)
        if not consignees:
            consignee_default = '1'
        else:
            consignee_default = '0'
        
        consignee = cls.objects.create(user=user,
                                        consignee_name=consignee_name,
                                        consignee_phone=consignee_phone,
                                        consignee_address=consignee_address,
                                        consignee_region=consignee_region,
                                        consignee_default=consignee_default)
        consignee.save()
        return consignee
    def update(self, data):
        self.user = data['user']
        self.consignee_name = data['consignee_name']
        self.consignee_phone = data['consignee_phone']
        self.consignee_address = data['consignee_address']
        self.consignee_region = data['consignee_region']
        self.save()


    def get_dict(self):
        return dict(consignee_name=self.consignee_name,
                    consignee_phone=self.consignee_phone,
                    consignee_address=self.consignee_address,
                    consignee_id=self.id,
                    consignee_default=self.consignee_default,
                    consignee_region=self.consignee_region)
   
class Order(models.Model):    
    methods = (('0','支付宝支付'),('1', '微信支付'),('2', '国付宝支付'), ('3', '交易宝支付'))
    results = (('0','交易失败'),('1', '交易成功'))
    delivery_choices = (('0','待支付'),('1', '待发货'),('2', '已发货'), ('3', '待评价'), ('4', '退款'))
    order_id = models.CharField(max_length=50, primary_key=True, verbose_name='订单号')
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE,verbose_name='用户')
    item_id = models.CharField(max_length=20, verbose_name='项目id')    
    support_money = models.FloatField(default=0,verbose_name='支持金额')
    trade_time = models.DateTimeField(auto_now_add=True, verbose_name='交易时间')
    trade_method = models.CharField(max_length=1, choices=methods, default='1', verbose_name='交易方式')
    trade_result = models.CharField(max_length=1, choices=results, default='0', verbose_name='交易结果')
    payback = models.CharField(max_length=10, verbose_name='是否接收产品回报') # '0'不接受回报， '1'接受回报
    delivery_status = models.CharField(max_length=1, choices=delivery_choices, verbose_name='发货状态')
    consignee_name = models.CharField(max_length=20, null=True, blank=True, verbose_name='收货人姓名')
    consignee_phone = models.CharField(max_length=11, null=True, blank=True, verbose_name='收货人电话')
    consignee_address = models.CharField(max_length=50, null=True, blank=True, verbose_name='收货人地址')
    class Meta:
        verbose_name = '订单'
        verbose_name_plural = verbose_name

    def get_bref_info(self):
        order_id = self.order_id
        support_user = self.user
        item_id = self.item_id
        support_money = self.support_money
        trade_time = trans_to_localtime(self.trade_time)
        trade_time = trade_time.strftime('%Y-%m-%d %H:%M:%S')
        info = dict(order_id=order_id,
                support_user=support_user.nick_name,
                item_id = item_id,
                support_money=support_money,
                trade_time=trade_time)
        return info

    def get_trade_time(self):
        return trans_to_localtime(self.trade_time).strftime('%Y-%m-%d %H:%M:%S')


        
    @classmethod
    def get_list(cls):
        orders = cls.objects.all()
        order_list = [order.get_bref_info() for order in orders]
        return order_list


    @classmethod
    def create(cls, data):
        print(data)
        identity = data['identity']
        user = MyUser.get_user_by_identity(identity)
        support_money = data['support_money']
        payback = data['payback']
#        trade_method = data['trade_method']
        item_id = data['item_id']
        order_id = str(datetime.datetime.now().strftime('%Y%m%d%H%M%s')) + str(user.id) + str(item_id)

        order = cls.objects.create(
                order_id = order_id,
                user=user,
                item_id=item_id, 
                support_money=support_money, 
                payback=payback,)
#                trade_method=trade_method)
        if payback == '1':
            order.consignee_name = data['consignee_name']
            order.consignee_phone = data['consignee_phone']
            order.consignee_address = data['consignee_address']
        order.save()
        


        return order 


    def __str__(self):
        return self.order_id

class TradeRecord(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE,verbose_name='用户')
    money_before = models.FloatField(default=0,verbose_name='交易前金额')
    money_now = models.FloatField(default=0,verbose_name='交易后金额')
    balance = models.FloatField(default=0,verbose_name='交易金额')
    trade_type = models.CharField(max_length=20, null=True, blank=True, verbose_name='交易类型') #cash提现， charge充值
    trade_time = models.DateTimeField(auto_now_add=True, verbose_name='交易时间')
    trade_status = models.CharField(max_length=20, default='wait_check', verbose_name='交易状态') #cashed已提现  cashing提现中 wait_check待审核
    bank = models.ForeignKey(BankCardInfo, on_delete=models.CASCADE,verbose_name='银行卡信息')

    def get_info(self):
        trade_time = trans_to_localtime(self.trade_time).strftime('%Y-%m-%d %H:%M:%S')
        return dict(trade_id=self.id,
                user_id=self.user.id,
                nick_name=self.user.nick_name,
                money_before=self.money_before,
                money_now=self.money_now,
                balance=self.balance,
                trade_type=self.trade_type,
                trade_status=self.trade_status,
                trade_time=trade_time)

    @classmethod
    def apply_cash(cls, data):
        identity = data.get('identity')
        user = MyUser.get_user_by_identity(identity)

        cash_money = float(data.get('cash_money'))

        money_before = user.balance
        money_now = user.balance-cash_money

        bank_id = data.get('bank_id')
        bank = BankCardInfo.objects.get(card_no=bank_id)

        record = cls.objects.create(user=user,
                money_before=money_before,
                money_now=money_now,
                balance=cash_money,
                trade_type='cash',
                bank=bank
                )


        user.balance -= cash_money
        user.save()
        return record

  
class RedPacket(models.Model):
    status_choices = (('0','未使用'),('1', '已过期'),('2', '已使用'))
    use_status = models.CharField(max_length=1, choices=status_choices, verbose_name='使用状态')
    money = models.IntegerField(verbose_name='价值')
    class Meta:
        verbose_name = '红包'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.money

