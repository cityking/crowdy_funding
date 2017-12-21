from django.db import models
from config.tool import trans_to_localtime, ndays_time, del_uploaded, is_img_or_video, get_screenshot
from crowdy_funding.personal_center.models import MyUser, Order, UserConsignee
from django.conf import settings
import json
import urllib 
from urllib.parse import urljoin
import datetime

#图片地址
bucket_domain = 'http://cdn.hopyun.com/'

# Create your models here.


class ItemType(models.Model):
    type_name = models.CharField(max_length=20, verbose_name='类型名称')
    type_log = models.CharField(max_length=100, null=True, blank=True,  verbose_name='类型图标')
    class Meta:
        verbose_name = '项目类型'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.type_name

    def get_dict(self):
        return dict(type_id=self.id, type_name=self.type_name, type_log=self.type_log) 

    def update(self, data):
        type_name = data.get('type_name')
        if type_name:
            self.type_name = type_name

        type_log = data.get('type_log')
        if type_log:
            key = self.type_log.split('/')[-1]
            del_uploaded(key)
            self.type_log = type_log

        self.save()

    def delete_type(self):
        
        type_log = self.type_log
        key = type_log.split('/')[-1]
        del_uploaded(key)
        self.delete()



    @classmethod
    def create(cls, data):
        type_name = data.get('type_name')
        type_log = data.get('type_log')
        item_type = cls.objects.create(type_name=type_name, type_log=type_log)
        return item_type


class ItemInfo(models.Model):
    type_choices = (('1','爱心救助'),('2','公益众筹'),('3', '梦想众筹'))
    status_choices = (('0','审核中'),('1','进行中'),('2', '审核未通过'), ('3', '已完成'), ('4', '已停止'))
    currency_choices = (('cny', '人民币'), ('vr','vr9'))

    initiator = models.ForeignKey(MyUser, models.SET_NULL,blank=True, null=True,related_name='initiator_user',  verbose_name='发起人')
    item_type = models.ForeignKey(ItemType,models.SET_NULL,blank=True, null=True,verbose_name='项目类型')
    item_name = models.CharField(max_length=20, verbose_name='项目名称')
    funding_money = models.FloatField(default=0,verbose_name='已筹金额')
    objective_money = models.FloatField(default=0,verbose_name='目标金额')
    currency = models.CharField(max_length=5, choices=currency_choices, verbose_name='币种')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='发起时间')
    total_time = models.IntegerField(default=0,verbose_name='项目时间')
    left_time = models.IntegerField(default=0,verbose_name='剩余时间')
    item_content = models.TextField(max_length=1000, verbose_name='项目内容')
    fund_use = models.TextField(max_length=200, verbose_name='资金用途')
    support_users = models.ManyToManyField(MyUser, related_name='suport_users', verbose_name='支持者')
    examination_status = models.CharField(max_length=20, default='0', choices=status_choices, verbose_name='审核状态')
    medias = models.CharField(max_length=1000, verbose_name='项目视频或图片地址')
    collect_users = models.ManyToManyField(MyUser, related_name='collect_users', verbose_name='收藏者')
    recommand = models.CharField(max_length=5, default='0', verbose_name='推荐') #0不推荐，1推荐 

    class Meta:
        verbose_name = '项目信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.item_name

    def delete_item(self):
        medias = eval(self.medias)
        for url in medias:
            key = url.split('/')[-1]
            del_uploaded(key)
        self.delete()


    def get_item_dict(self):
        schedule = '%.2f' % float(self.funding_money/self.objective_money)
        schedule = float(schedule)
        if schedule >= 1:
            schedule = 1

        news, update_time = self.get_item_latest_support()
        thumbs = Thumb_up.objects.filter(item=self).count()
        support_count = Order.objects.filter(item_id=self.id).filter(trade_result='1').count()
        user = self.initiator
        item_type = self.item_type
        type_id = item_type.id

        
        media_url = eval(self.medias)
        if not is_img_or_video(media_url[0])['is_img']:
            for url in media_url:
                if is_img_or_video(url)['is_img']:
                    index = media_url.index[url]
                    media_url[index] = media_url[0]
                    media_url[0] = url
                    break
            else:
                url = get_screenshot(media_url[0])
                media_url.append(media_url[0])
                media_url[0] = url
                
        self.medias = str(media_url)
        self.save() 
            
        
#        import re
#        if not re.match('\[.*\]$', media_url):
#            media_url = '["%s"]' % media_url
        item_list = {'item_id':self.id,
            'avatar':user.avatar_url,
            'nickname':user.nick_name,
            'examination_status':self.examination_status, 
            'item_name':self.item_name, 
            'item_content': self.item_content,
            'item_type':str(self.item_type),
            'type_id':type_id,
            'funding_money':self.funding_money,
            'support_users_count':support_count,
            'media_url':media_url,
            'schedule':schedule,
            'currency':self.currency,
            'create_time':self.create_time,
            }

        return item_list

    def get_item_bref(self):
        create_time = trans_to_localtime(self.create_time)
        create_time = create_time.strftime('%Y-%m-%d %H:%M:%S')
        item_list = {
            'item_id':self.id,
            'create_time': create_time,
            'nickname':self.initiator.nick_name,
            'examination_status':self.examination_status, 
            'item_name':self.item_name, 
#            'recommand':self.recommand
        }

        return item_list


    def get_item_detail(self, user):
        item_detail = self.get_item_dict()
        item_detail['objective_money'] = self.objective_money
        item_detail['left_time'] = self.left_time
        item_detail['fund_use'] = self.fund_use

        rebacks = PayBack.objects.filter(item=self)
        reback_list = [{'payback_id':reback.id, 'reback_money':reback.money, 'reback_content':reback.content} for reback in rebacks]
        if reback_list:
            is_reback = '1'
        else:
            is_reback = '0'
        item_detail['is_reback'] = is_reback
        item_detail['reback'] = reback_list
        item_detail['create_time'] = self.create_time 
        order_list = Order.objects.filter(item_id=self.id).filter(trade_result='1').order_by('-trade_time')
        support_list = []
        for order in order_list:
            order_id = order.order_id
            comments = Comment.objects.filter(order=order).count()
            thumbs = Thumb_up.objects.filter(order=order).count()
            try:
                thumb = Thumb_up.objects.filter(order=order).get(user=user)
                is_thumbed = 1
            except Exception as e:
                is_thumbed = 0
            trade_time = trans_to_localtime(order.trade_time).strftime('%Y-%m-%d %H:%M:%S')
            support_list.append({ 
                    'avatar':order.user.avatar_url, 
                    'user_name':order.user.nick_name, 
                    'support_money':order.support_money, 
                    'trade_time':trade_time, 
                    'order_id':order_id,
                    'comments':comments, 
                    'thumbs':thumbs, 
                    'currency':self.currency,
                    'is_thumbed':is_thumbed})
        item_detail['support_list']=support_list

        collect_users = self.collect_users.all()
        if user in collect_users:
            collected = '1'
        else:
            collected = '0'

        item_detail['collected'] = collected
        return item_detail
    def get_manage_info(self):
        objective_money = self.objective_money
        funding_money = self.funding_money
        support_users_count = self.support_users.all().count()
        left_time = self.left_time
        media_url = eval(self.medias)
        item_name = self.item_name
        item_content = self.item_content
        currency = self.currency

        order_list = Order.objects.filter(item_id=self.id).filter(trade_result='1').order_by('-trade_time')
        now_time = datetime.datetime.now()
        now_time = now_time.strftime('%Y-%m-%d')
        today_orders = order_list.filter(trade_time__gt=now_time)
        today_money = 0
        for order in today_orders:
            today_money += order.support_money
        payback_orders = order_list.filter(payback='1') 
        payback_list = []
        for order in payback_orders:
            try:
                payback = UserPayBack.objects.filter(delete_status='0').get(order=order)
                payback_list.append(payback.get_bref_info())
            except:
                continue
            

        data = dict(objective_money=objective_money,
                funding_money=funding_money,
                support_users_count=support_users_count,
                left_time=left_time,
                media_url=media_url,
                item_name=item_name,
                item_content=item_content,
                currency=currency,
                today_money=today_money,
                payback_list=payback_list)

        return data 

    def get_item_bref_detail(self):
        create_time = trans_to_localtime(self.create_time)
        create_time = create_time.strftime('%Y-%m-%d %H:%M:%S')

        schedule = self.funding_money/self.objective_money
        if schedule >= 1:
            schedule = 1
        news = self.get_item_latest_support()
        thumbs = Thumb_up.objects.filter(item=self).count()
        rebacks = PayBack.objects.filter(item=self)
        reback_list = [{'reback_money':reback.money, 'reback_content':reback.content} for reback in rebacks]
        if reback_list:
            is_reback = '1'
        else:
            is_reback = '0'
        media_url = self.medias
        import re
        if not re.match('\[.*\]$', media_url):
            media_url = '["%s"]' % media_url

   
        item_list = {'item_id':self.id,
            'create_time': create_time,
            'nickname':self.initiator.nick_name,
            'examination_status':self.examination_status, 
            'item_name':self.item_name, 
            'item_content': self.item_content,
            'fund_use': self.fund_use,
            'funding_money':self.funding_money,
            'objective_money':self.objective_money,
            'support_users_count':self.support_users.count(),
            'schedule':schedule,
            'currency':self.currency,
            'left_time':self.left_time,
            'last_time':self.total_time,
            'media_url':eval(media_url),
            'mobile':self.initiator.mobile,
            'item_type':self.item_type.id,
            'item_type_name':self.item_type.type_name,
            'is_reback':is_reback,
            'reback':reback_list,
            'recommand':self.recommand,
            }

        return item_list

    def get_item_latest_support(self):
        item_id = self.id
        orders = Order.objects.filter(item_id=item_id)
        if orders:
            order = orders[0]
        else:
            return 'none', 'none' 
        user = order.user
        user_name = user.nick_name
        trade_time = trans_to_localtime(order.trade_time)
        trade_time = trade_time.strftime('%Y-%m-%d %H:%M')
        print(type(trade_time))
        support_money = order.support_money
        if self.currency == 'vr':
            message = 'VR积分'
        else:
            message = self.currency.upper()
        
        news = '%s 于%s支持了 %s%s' % (user_name, trade_time, support_money, message)
        return news, trade_time 
    def update(self, data):
        try:
            print(data)
            item_type = data.get('item_type')    
            if item_type:
                item_type = ItemType.objects.get(id=item_type)
                self.item_type = item_type

            examination_status = data.get('examination_status')
            if examination_status:
                self.examination_status = examination_status
            
            objective_money = data.get('objective_money')
            if objective_money:
                self.objective_money = objective_money
            item_name = data.get('item_name')
            if item_name:
                self.item_name = item_name
            item_content = data.get('item_content') 
            if item_content:
                self.item_content = item_content
            is_reback = data.get('is_reback')
            urls = data.get('media_url', '')
            import re
            if re.match('\[.*\]',urls):
                media_url = []
                if urls:
                    urls = eval(urls)
                    print(urls)
                    for url in urls:
                        if bucket_domain not in url:
                            url = urljoin(bucket_domain, url)
                        media_url.append(url)
                        
                media_url = str(media_url)            
            else:
                media_url = urljoin(bucket_domain, urls)
            if media_url:
                old_medias = eval(self.medias)
                for url in old_medias:
                    if url not in eval(media_url):
                        key = url.split('/')[-1]
                        del_uploaded(key)
                self.medias = media_url
            fund_use = data.get('fund_use')
            if fund_use:
                self.fund_use = fund_use
            total_time = data.get('last_time')
            if total_time:
                self.total_time = total_time
                left_time = total_time
                if left_time:
                    self.left_time = left_time
           # currency = data.get('currency')
            self.currency = 'CNY'
            if is_reback == '1':
                paybacks = PayBack.objects.filter(item=self)
                if paybacks:
                    paybacks.delete()

                rebacks = data.get('reback')

                rebacks = json.loads(rebacks)
                for reback in rebacks:
                    payback = PayBack.objects.create(money=reback['reback_money'], content=reback['reback_content'], item=self)
                    payback.save()
            elif is_reback == '0':
                paybacks = PayBack.objects.filter(item=self)
                if paybacks:
                    paybacks.delete()
            self.save()
        except Exception:
            return None
        return self 

        
    @classmethod
    def create(cls, data, user): 
        try:
            print(data)
            item_type = data.get('item_type')    
            item_type = ItemType.objects.get(id=item_type)
            objective_money = data.get('objective_money')
            item_name = data.get('item_name')
            item_content = data.get('item_content') 
            is_reback = data.get('is_reback')
            urls = data.get('media_url', '')
            import re
            if re.match('\[.*\]',urls):
                media_url = []
                if urls:
                    urls = eval(urls)
                    print(urls)
                    for url in urls:
                        url = urljoin(bucket_domain, url)
                        media_url.append(url)
                        
                media_url = str(media_url)            
            else:
                media_url = urljoin(bucket_domain, urls)
            fund_use = data.get('fund_use')
            total_time = data.get('last_time')
            left_time = total_time
           # currency = data.get('currency')
            currency = 'CNY'
            item = cls.objects.create(initiator=user,
                                item_type=item_type,
                                objective_money=objective_money,
                                currency = currency,
                                total_time=total_time,
                                left_time=left_time,
                                item_name=item_name,
                            item_content=item_content,
                            fund_use=fund_use,
                            medias=media_url)
            item.save()
            if is_reback == '1':
                rebacks = data.get('reback')
                rebacks = json.loads(rebacks)
                for reback in rebacks:
                    payback = PayBack.objects.create(money=reback['reback_money'], content=reback['reback_content'], item=item)
                    payback.save()
        except Exception:
            return None
        return item

    

class PayBack(models.Model):
    money = models.FloatField(default=0,verbose_name='回报金额')
    content = models.CharField(max_length=20, verbose_name='回报内容')
    is_delivery = models.CharField(max_length=2, default='0', verbose_name='是否要快递') #'0'不需要快递，'1'需要快递
    item = models.ForeignKey(ItemInfo,models.SET_NULL,blank=True, null=True,verbose_name='回报项目')
    class Meta:
        verbose_name = '回报'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content
class DeliveryCompany(models.Model):
    name = models.CharField(max_length=20, verbose_name='名称')

    class Meta:
        verbose_name = '快递公司'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

payback_status = (('0','待回报'), ('1','已回报'))
class UserPayBack(models.Model):
    order = models.ForeignKey(Order, verbose_name='支持订单')
    payback = models.ForeignKey(PayBack, verbose_name='回报内容')
    status = models.CharField(max_length=2, choices=payback_status, verbose_name='回报状态') 
    consignee = models.ForeignKey(UserConsignee, verbose_name='回报地址')
    delivery_company = models.CharField(max_length=15, null=True, blank=True, verbose_name='快递公司')
    delivery_id = models.CharField(max_length=15, null=True, blank=True, verbose_name='快递单号')
    delete_status = models.CharField(max_length=2, default='0', verbose_name='删除状态') #'0' 未删除 '1' 已删除
    content = models.CharField(max_length=15, null=True, blank=True, verbose_name='回报内容')

    class Meta:
        verbose_name = '用户回报'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.payback.content

    def get_bref_info(self):
        user = self.order.user
        avatar = user.avatar_url
        nick_name = user.nick_name
        support_money = self.order.support_money
        trade_time = self.order.trade_time
        trade_time = trans_to_localtime(trade_time).strftime('%Y-%m-%d %H:%M:%S')
        status = self.status

        return dict(payback_id=self.id,
                avatar=avatar,
                nick_name=nick_name,
                support_money=support_money,
                trade_time=trade_time,
                status=status)
    def get_info(self):
        user = self.order.user
        avatar = user.avatar_url
        nick_name = user.nick_name
        support_money = self.order.support_money
        

        consignee = self.consignee
        consignee_name = consignee.consignee_name
        consignee_phone = consignee.consignee_phone
        consignee_region = consignee.consignee_region
        consignee_address = consignee.consignee_address

        content = self.payback.content
        is_delivery = self.payback.is_delivery
        return dict(avatar=avatar,
                nick_name=nick_name,
                support_money=support_money,
                consignee_name=consignee_name,
                consignee_phone=consignee_phone,
                consignee_address=consignee_address,
                consignee_region=consignee_region,
                is_delivery=is_delivery,
                content=content
                )

    def get_order_info(self):
        order = self.order
        trade_time = trans_to_localtime(order.trade_time).strftime('%Y-%m-%d %H:%M:%S')
        delivery_status = order.delivery_status
        support_money = order.support_money

        item_id = order.item_id
        item = ItemInfo.objects.get(id=item_id)
        medias = eval(item.medias)
        item_name = item.item_name
        content = self.payback.content
        number = 1
        end_time = trans_to_localtime(ndays_time(int(item.left_time))).strftime('%Y-%m-%d %H:%M:%S')
        
        return dict(payback_id = self.id,
                delivery_status=delivery_status,
                trade_time=trade_time,
                support_money=support_money,
                media_url = medias,
                item_name=item_name,
                content = content,
                number = number,
                end_time = end_time
                )
    def get_order_detail(self):
        info = self.get_order_info()
        consignee = self.consignee
        user = self.order.user
        nick_name = user.nick_name
        avatar = user.avatar_url

        data = dict(delivery_company = self.delivery_company,
            nick_name=nick_name,
            avatar = avatar,
            delivery_id = self.delivery_id,
            consignee_name = consignee.consignee_name,
            consignee_phone = consignee.consignee_phone,
            consignee_region = consignee.consignee_region,
            consignee_address = consignee.consignee_address)
        info.update(data)
        return info

    @classmethod
    def get_paybacks_by_user(cls,user):
        orders = Order.objects.filter(user=user)
        payback_list = []
        for order in orders:
            try:
                payback = cls.objects.filter(delete_status='0').get(order=order)
                payback_list.append(payback) 
            except:
                continue
        payback_list = [payback.get_order_info() for payback in payback_list]
        return payback_list


def get_user_item(user, status='0'):
    if status == '1':
        user_items = ItemInfo.objects.filter(initiator=user).exclude(examination_status='3').exclude(examination_status='4')
    elif status == '2':
        user_items = ItemInfo.objects.filter(initiator=user).exclude(examination_status='0').exclude(examination_status='1').exclude(examination_status='2')
    else:
        user_items = ItemInfo.objects.filter(initiator=user).filter(examination_status='1')
    item_list = []
    for item in user_items:
        item_list.append(item.get_item_dict())
    print(item_list)
    return item_list 

def get_user_support_items(user):
    all_items = ItemInfo.objects.all().filter(examination_status='1')
    #all_items = ItemInfo.objects.filter(support_users__contains=user)
    #item = all_items[0]
    user_items = [item.get_item_dict()  for item in all_items if user in item.support_users.all()]
    return user_items

def get_collections(user):
    items = ItemInfo.objects.all()
    item_list = []
    for item in items:
        if user in item.collect_users.all():
            item_list.append(item.get_item_dict())
    return item_list

class Comment(models.Model):
    order = models.ForeignKey(Order, verbose_name='订单')
    user = models.ForeignKey(MyUser,related_name='commnet_user', verbose_name='用户')
    item = models.ForeignKey(ItemInfo, verbose_name='项目' )
    support_user = models.ForeignKey(MyUser,related_name='comment_support_user', null=True, verbose_name='支持者')
    content = models.CharField(max_length=200, verbose_name='评论内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    up_comment = models.ForeignKey('self', blank=True, null=True, default=None)
    class Meta:
        verbose_name = '评论信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content

    def get_info(self):
        user = self.user
        create_time = trans_to_localtime(self.create_time)
        create_time = create_time.strftime('%Y-%m-%d %H:%M:%S')
        sub_comments = Comment.objects.filter(up_comment=self)
        comments = []
        for comment in sub_comments:
            comments.append(comment.get_info())
        
            
        result = {'order_id':self.order.order_id, 'comment_id':self.id, 'avatar':user.avatar_url, 'nickname':user.nick_name, 'create_time':create_time, 'content':self.content, 'subcomments':comments}
        
        return result 
    
    @classmethod
    def get_item_comments(cls, item):
        comments = cls.objects.filter(item=item).order_by('create_time')
        result = []
        for comment in comments:
            result.append(comment.get_info())
        return result

    @classmethod
    def get_comments(cls, user):
        comments = cls.objects.filter(up_comment__user=user).order_by('-create_time').exclude(user=user)
        result = []
        for comment in comments:
            up_comment = comment.up_comment
            up_comment_info = up_comment.get_info()
            up_comment_info['subcomments'] = []
            comment_info = comment.get_info()
            info = dict(up_comment=up_comment_info,
                    comment_info=comment_info)
            result.append(info)
            
        return result

class Thumb_up(models.Model):
    order = models.ForeignKey(Order, verbose_name='订单')
    user = models.ForeignKey(MyUser,related_name='thumbs_user',verbose_name='用户')
    item = models.ForeignKey(ItemInfo, verbose_name='项目' )
    support_user = models.ForeignKey(MyUser,related_name='thumbs_support_user', verbose_name='支持者')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    class Meta:
        verbose_name = '点赞信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user_id

class Report(models.Model):
    user = models.ForeignKey(MyUser,related_name='report_user',verbose_name='用户')
    item = models.ForeignKey(ItemInfo, verbose_name='项目' )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    reason = models.CharField(max_length=200, verbose_name='举报理由')
    images = models.CharField(max_length=200, verbose_name='举报图片')
    class meta:
        verbose_name = '举报信息'
        verbose_name_plural = verbose_name

    @classmethod
    def create(cls, data):
        report = cls.objects.create(user=data['user'],
                                    item = data['item'],
                                    reason = data['reason'],
                                    images = data['images'])
        report.save()
        return report

    def get_info(self):
        create_time = trans_to_localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')
        return dict(user_id=self.user.id,
                nick_name=self.user.nick_name,
                item_id=self.item.id,
                item_name=self.item.item_name,
                reason=self.reason,
                images=eval(self.images),
                create_time=create_time)


