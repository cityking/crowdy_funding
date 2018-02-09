from django.shortcuts import render
from .models import * 
from django.http import JsonResponse,HttpResponse
from crowdy_funding.project_content.models import *
from crowdy_funding.personal_center.models import *
from datetime import datetime
from config.tool import *
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.
@csrf_exempt
def admin_login(request):
    if request.method == 'POST':
        try:
            data = request.body
            data = data.decode()
            try:
                data = json.loads(data)
                nick_name = data.get('nick_name')
                password = data.get('password')
                identity = Adminastrator.admin_login(nick_name, password)
                if identity == '1':
                    result = {'status':'400', 'message':'管理员不存在', 'content':'none'}
                elif identity == '0':
                    result = {'status':'400', 'message':'密码错误', 'content':'none'}
                else:
                    adminastrator = Adminastrator.objects.get(nick_name=nick_name)
                    data = {'identity':identity, 'nick_name':nick_name, 'authority':adminastrator.authority}
                    result = {'status':'200', 'message':'登录成功', 'content':data}

            except Exception as e:
                log_exception()
                result = {'status':'400', 'message':'json数据解析错误 %s' % data, 'content':'none'}
                return JsonResponse(result, safe=False)

           
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False)
@csrf_exempt
@admin_authentication
def add_adminastrator(request):
    if request.method == 'POST':
        try:
            data = request.body
            data = data.decode()
            data = json.loads(data)
            try:
                identity = data.get('identity')
                adminastrator = Adminastrator.get_adminastrator_by_identity(identity)
                if adminastrator.authority == 'super':
                    nick_name = Adminastrator.add(data)

                    if nick_name == '0':
                        result = {'status':'400', 'message':'两次密码输入不一样', 'content':'none'}
                    elif nick_name == '1':
                        result = {'status':'400', 'message':'管理员已存在', 'content':'none'}
                    elif nick_name == '2':
                        result = {'status':'400', 'message':'nick_name不能为空', 'content':'none'}
                    elif nick_name == '3':
                        result = {'status':'400', 'message':'密码不能为空', 'content':'none'}
                    elif nick_name == '3':
                        result = {'status':'400', 'message':'添加失败', 'content':'none'}

                    else:
                        result = {'status':'200', 'message':'管理员%s添加成功' % nick_name, 'content':'none'}
                else:
                    result = {'status':'400', 'message':'权限不足', 'content':'none'}

            except Exception as e:
                log_exception()
                result = {'status':'400', 'message':'json数据解析错误 %s' % data, 'content':'none'}
                return JsonResponse(result, safe=False)

           
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False)

@admin_authentication
def get_adminastrators_info(request):
    if request.method == 'GET':
        try:
            adminastrators = Adminastrator.objects.all()
            if adminastrators:
                adminastrators = [adminastrator.get_info() for adminastrator in adminastrators]
                result = {'status':'200', 'message':'获取成功', 'content':adminastrators}
            else:
                result = {'status':'400', 'message':'没有管理员', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False)
@admin_authentication
def get_adminastrator_info(request):
    if request.method == 'GET':
        try:
            identity = request.GET.get('identity')
            adminastrator = Adminastrator.get_adminastrator_by_identity(identity)
            if adminastrator:
                data = adminastrator.get_info()
                result = {'status':'200', 'message':'获取成功', 'content':data}
            else:
                result = {'status':'400', 'message':'没有此管理员', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False)

@admin_authentication
def del_adminastrator(request):
    if request.method == 'GET':
        try:
            identity = request.GET.get('identity')
            nick_name = request.GET.get('nick_name')
            adminastrator = Adminastrator.get_adminastrator_by_identity(identity)
            if adminastrator.authority == 'super' and nick_name != adminastrator.nick_name:
                adminastrator = Adminastrator.objects.get(nick_name=nick_name)
                if adminastrator:
                    adminastrator.delete()
                    result = {'status':'200', 'message':'删除成功', 'content':'none'}
                else:
                    result = {'status':'400', 'message':'没有此管理员', 'content':'none'}
            else:
                result = {'status':'400', 'message':'权限不足', 'content':'none'}


        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False)

@admin_authentication
def update_password(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            identity = data.get('identity')
            adminastrator = Adminastrator.get_adminastrator_by_identity(identity)
            if not adminastrator.is_super():
                result = {'status':'400', 'message':'权限不足', 'content':'none'}
                return JsonResponse(result, safe=False)
            
            nick_name = data.get('nick_name')
            password = data.get('password')
            adminastrator = Adminastrator.objects.get(nick_name=nick_name)
            if password:
                adminastrator.password = make_password(password)
                adminastrator.save()
                result = {'status':'200', 'message':'修改成功', 'content':'none'}
            else:
                result = {'status':'400', 'message':'密码不能为空', 'content':'none'}
            
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False) 

@pagination
@admin_authentication
def item_list(request):
    if request.method == 'GET':
        try:
            items = ItemInfo.objects.all().order_by('-create_time')
            key = request.GET.get('key')
            if key:
                items = items.filter(item_name__contains=key).order_by('-create_time')
            examination_status = request.GET.get('status')
            if examination_status:
                items = items.filter(examination_status=examination_status).order_by('-create_time')
            recommand = request.GET.get('recommand')
            if recommand == '1':
                items = items.filter(recommand='1')

            item_list = []
            for item in items:
                item_list.append(item.get_item_bref_detail())


            result = {'status':'200', 'message':'success', 'content':item_list} 
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'} 
        print(result)

        return JsonResponse(result, safe=False)
    else:
        response = JsonResponse(None, safe=False)
        return response 

@admin_authentication
def item_bref_detail(request):
    if request.method == 'GET':
        try:
            item_id = request.GET.get('item_id')
            item = ItemInfo.objects.get(id=item_id)
            item_detail = item.get_item_bref_detail()
            result = {'status':'200', 'message':'success', 'content':item_detail} 
        except Exception as e:
            log_exception()
            print(e)
            result = {'status':'400', 'message':'', 'content':'none'} 
        return JsonResponse(result, safe=False)
    else:
        response = JsonResponse(None, safe=False)
        return response 

@admin_authentication
def del_item(request):
    if request.method == 'GET':
        try:
            item_id = request.GET.get('item_id')
            item = ItemInfo.objects.get(id=item_id)
            if item: 
                if item.examination_status != '1':
                    item.delete_item()
                    
                    result = {'status':'200', 'message':'删除成功', 'content':'none'}
                else:
                    result = {'status':'400', 'message':'项目正在进行，不能删除', 'content':'none'}
            else:
                result = {'status':'400', 'message':'项目不存在', 'content':'none'}
                
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)


@admin_authentication
def get_support_list(request):
    if request.method == 'GET':
        try:
            support_list = Order.get_list()
            for info in support_list:
                item_id = info['item_id']
                item = ItemInfo.objects.get(id=item_id)
                info['item_name'] = item.item_name
            result = {'status':'200', 'message':'获取成功', 'content':support_list}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False)

@csrf_exempt
@admin_authentication
def update_item(request):
    if request.method == 'POST':
        try:
            data = request.POST.dict()
            item_id = data.get('item_id')
            item = ItemInfo.objects.get(id=item_id)
            images = data.get('ori_img')
            reback = data.get('reback')
            if reback:
                data['reback'] = eval(reback)
            if not images:
                images = []
            else:
                images = eval(images)

            files = request.FILES.getlist('img')
            bucket_domain = 'http://cdn.hopyun.com/'
            if files:
                for _file in files:
                    url = upload_file(_file.file.read(), name=_file.name)
                    url = urljoin(bucket_domain, url)
                    print(url)
                    images.append(url)
            data['media_url'] = str(images)
            item.update(data)
            result = {'status':'200', 'message':'修改成功', 'content':'none'}
        except Exception as e:
            log_exception()
            print(e)
            result = {'status':'400', 'message':'', 'content':'none'}

        print(result)
        return JsonResponse(result, safe=False)
    else:
        response = JsonResponse(None, safe=False)
        return response

@csrf_exempt
@admin_authentication
def update_item_status(request):
    if request.method == 'POST':
        try:
            data = request.body
            data = data.decode()
            data = json.loads(data)
           
            item_id = data.get('item_id')
            item = ItemInfo.objects.get(id=item_id)
            examination_status = str(data.get('status'))
            if examination_status:
                if examination_status=='1': 
                    user = item.initiator
                    items = ItemInfo.objects.filter(initiator=user).filter(examination_status='1')
                    if items:
                        result = {'status':'400', 'message':'你还有其他项目在进行', 'content':'none'}
                        return JsonResponse(result, safe=False)
                        
                    item.examination_time = datetime.now()
                item.examination_status = examination_status
                item.save()
                result = {'status':'200', 'message':'修改成功', 'content':'none'}
            else:
                result = {'status':'400', 'message':'未传入状态', 'content':'none'}
                    
        except Exception as e:
            log_exception()
            print(e)
            result = {'status':'400', 'message':traceback.print_exc(), 'content':'none'}

        print(result)
        return JsonResponse(result, safe=False)
    else:
        response = JsonResponse(None, safe=False)
        return response

@csrf_exempt
@admin_authentication
def add_announce(request):
    if request.method == 'POST':
        try:
            data = request.body
            data = data.decode()
            data = json.loads(data)
            announce = Announcement.create(data)
            if announce:
                if announce == '0':
                    result = {'status':'400', 'message':'标题不能为空', 'content':'none'}
                elif announce == '1':
                    result = {'status':'400', 'message':'内容不能为空', 'content':'none'}
                else:
                    result = {'status':'200', 'message':'添加成功', 'content':'none'}
            else:
                result = {'status':'400', 'message':'添加失败', 'content':'none'}

        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False)
@csrf_exempt
@admin_authentication
def update_announce(request):
    if request.method == 'POST':
        try:
            data = request.body
            data = data.decode()
            data = json.loads(data)
            announce_id = data.get('announce_id')
            announce = Announcement.objects.get(id=announce_id)
            announce = announce.update(data)
            result = {'status':'200', 'message':'修改成功', 'content':'none'}

        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False)

@csrf_exempt
@admin_authentication
def delete_announce(request):
    if request.method == 'POST':
        try:
            data = request.body
            data = data.decode()
            data = json.loads(data)
            announce_id = data.get('announce_id')
            announce = Announcement.objects.get(id=announce_id)
            if announce:
                announce.delete()
            result = {'status':'200', 'message':'删除成功', 'content':'none'}

        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False)



@admin_authentication
def get_announce_list(request):
    if request.method == 'GET':
        try:
            announce_list = Announcement.objects.all().order_by('-create_time')
            announce_list = [announce.get_info() for announce in announce_list]
            result = {'status':'200', 'message':'获取成功', 'content':announce_list}

        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False)

@admin_authentication
def get_announce(request):
    if request.method == 'GET':
        try:
            announce_id = request.GET.get('announce_id')
            announce = Announcement.objects.get(id=announce_id)
            content = announce.get_info()
            result = {'status':'200', 'message':'获取成功', 'content':content}

        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False)

@csrf_exempt
@admin_authentication
def add_item_type(request):
    if request.method == 'POST':
        try:
            data = request.POST.dict()

            files = request.FILES.getlist('type_log')
            bucket_domain = 'http://cdn.hopyun.com/'
            if files:
                for _file in files:
                    url = upload_file(_file.file.read())
                    url = urljoin(bucket_domain, url)
                    data['type_log'] = url

            item_type = ItemType.create(data)
  
            result = {'status':'200', 'message':'添加成功', 'content':'none'}

        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False)

@csrf_exempt
@admin_authentication
def del_item_type(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            type_id = data.get('type_id')
            item_type = ItemType.objects.get(id=type_id)
            items = ItemInfo.objects.filter(item_type=item_type)
            if not items:
                item_type.delete_type() 
                result = {'status':'200', 'message':'删除成功', 'content':'none'}
            else:
                result = {'status':'400', 'message':'该项目类型下面存在项目，不能删除', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False)

@csrf_exempt
@admin_authentication
def update_item_type(request):
    if request.method == 'POST':
        try:
            data = request.POST.dict()
            type_id = data.get('type_id')
            item_type = ItemType.objects.get(id=type_id)

            files = request.FILES.getlist('type_log')
            bucket_domain = 'http://cdn.hopyun.com/'
            if files:
                for _file in files:
                    url = upload_file(_file.file.read())
                    url = urljoin(bucket_domain, url)
                    data['type_log'] = url

            item_type.update(data)

  
            result = {'status':'200', 'message':'添加成功', 'content':'none'}

        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False)


@admin_authentication
def get_user_list(request):
    if request.method == 'GET':
        try:
            users = MyUser.objects.all().order_by('-join_date')
            user_list = [user.get_bref() for user in users]
            result = {'status':'200', 'message':'获取成功', 'content':user_list}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False)

@admin_authentication
def lock_user(request):
    if request.method == 'GET':
        try:
            user_id = request.GET.get('user_id')
            user = MyUser.objects.get(id=user_id)
            if user:
                if user.state==1:
                    result = {'status':'400', 'message':'会员已被锁定', 'content':'none'}
                else:
                    user.state='1'
                    user.save()
                    result = {'status':'200', 'message':'锁定成功', 'content':'none'}
            else:
                result = {'status':'400', 'message':'没有找到该会员', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False)

@admin_authentication
def unlock_user(request):
    if request.method == 'GET':
        try:
            user_id = request.GET.get('user_id')
            user = MyUser.objects.get(id=user_id)
            if user:
                if user.state==0:
                    result = {'status':'400', 'message':'会员未被锁定', 'content':'none'}
                else:
                    user.state='0'
                    user.save()
                    result = {'status':'200', 'message':'解锁成功', 'content':'none'}
            else:
                result = {'status':'400', 'message':'没有找到该会员', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False)


@admin_authentication
def get_payment_list(request):
    if request.method == 'GET':
        try:
            start_time = request.GET.get('start_time')
            if start_time:
                end_time = request.GET.get('end_time')
                if not end_time:
                    result = {'status':'400', 'message':'未传入结束时间', 'content':'none'}
                    return JsonResponse(result, safe=False)
                end_time = end_time + ' 23:59:59'
                orders = Order.objects.filter(trade_time__gt=start_time).filter(trade_time__lt=end_time).order_by('-trade_time').filter(trade_result='1')
            else:
                orders = Order.objects.filter(trade_result='1').order_by('-trade_time')
            payment_list = []
            for order in orders:
                item = ItemInfo.objects.get(id=order.item_id)
                initiator = item.initiator
                support_user = order.user
                trade_time = order.get_trade_time()
                money = order.support_money
                pay = dict(user_id=support_user.id,
                        nick_name=support_user.nick_name,
                        item_id=order.item_id,
                        item_name=item.item_name,
                        pay_method='pay',
                        money=money,
                        trade_time=trade_time)
                income = dict(user_id=initiator.id,
                        nick_name=initiator.nick_name,
                        item_id=order.item_id,
                        item_name=item.item_name,
                        pay_method='income',
                        money=money,
                        trade_time=trade_time)
                payment_list.append(pay)
                payment_list.append(income)
            result = {'status':'200', 'message':'获取成功', 'content':payment_list}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}     
        return JsonResponse(result, safe=False)

@admin_authentication
def get_support_list(request):
    if request.method == 'GET':
        try:
            start_time = request.GET.get('start_time')
            if start_time: 
                end_time = request.GET.get('end_time')
                if end_time:
                    end_time += ' 23:59:59'
                else:
                    result = {'status':'400', 'message':'未传入结束时间', 'content':'none'}
                    return JsonResponse(result, safe=False)
                orders = Order.objects.filter(trade_time__gt=start_time).filter(trade_time__lt=end_time).order_by('-trade_time').filter(trade_result='1')
            else:
                orders = Order.objects.filter(trade_result='1').order_by('-trade_time') 
            support_list = []
            for order in orders:
                item = ItemInfo.objects.get(id=order.item_id)
                initiator = item.initiator
                support_user = order.user
                trade_time = order.get_trade_time()
                money = order.support_money
                pay = dict(user_id=support_user.id,
                        nick_name=support_user.nick_name,
                        item_id=order.item_id,
                        item_name=item.item_name,
                        support_money=money,
                        trade_time=trade_time)
                support_list.append(pay)
            result = {'status':'200', 'message':'获取成功', 'content':support_list}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}     
        return JsonResponse(result, safe=False)

@csrf_exempt
@admin_authentication
def add_carousel(request):
    if request.method == 'POST':
        try:
            item_id = request.POST.get('item_id')
            item = ItemInfo.objects.get(id=item_id)

            files = request.FILES.getlist('carousel_img')
            bucket_domain = 'http://cdn.hopyun.com/'
            carousel_img = None
            if files:
                for data in files:
                    url = upload_file(data.file.read())
                    url = urljoin(bucket_domain, url)
                    print(url)
                    carousel_img = url

            carousel = Carousel.objects.create(item=item, carousel_img=carousel_img)
            result = {'status':'200', 'message':'添加成功', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message': '', 'content':'none'}

        print(result)
        return JsonResponse(result, safe=False)
    else:
        response = JsonResponse(None, safe=False)
        return response

@csrf_exempt
@admin_authentication
def del_carousel(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data) 
            carousel_id = data.get('carousel_id')
            carousel = Carousel.objects.get(id=carousel_id)
            carousel_img = carousel.carousel_img
            key = carousel_img.split('/')[-1]
            del_uploaded(key)
            carousel.delete() 
            result = {'status':'200', 'message':'删除成功', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message': '', 'content':'none'}

        print(result)
        return JsonResponse(result, safe=False)
    else:
        response = JsonResponse(None, safe=False)
        return response

@admin_authentication
def get_carousel_list(request):
    if request.method == 'GET':
        try:
            carousel_list = Carousel.objects.all()
            carousel_list = [carousel.get_info() for carousel in carousel_list]
            result = {'status':'200', 'message':'获取成功', 'content':carousel_list}

        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False)

@csrf_exempt
@admin_authentication
def update_item_fee(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            item_fee = data.get('item_fee')
            fee = Fee.objects.get(fee_type='item')
            fee.fee_money = item_fee
            fee.save()
            result = {'status':'200', 'message':'更改成功', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message': '', 'content':'none'}

        print(result)
        return JsonResponse(result, safe=False)
 
@csrf_exempt
@admin_authentication
def update_charge_fee(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            charge_fee = data.get('charge_fee')
            fee = Fee.objects.get(fee_type='charge')
            fee.fee_money = charge_fee
            fee.save()
            result = {'status':'200', 'message':'更改成功', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message': '', 'content':'none'}

        print(result)
        return JsonResponse(result, safe=False)
           
@admin_authentication
def get_fees(request):
    if request.method == 'GET':
        try:
            charge_fee = Fee.objects.get(fee_type='charge')
            item_fee = Fee.objects.get(fee_type='item')
            content = dict(item_fee = item_fee.fee_money,
                    charge_fee = charge_fee.fee_money)
            result = {'status':'200', 'message':'获取成功', 'content':content}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message': '', 'content':'none'}

        print(result)
        return JsonResponse(result, safe=False)
           
@admin_authentication
def get_report_list(request):
    if request.method == 'GET':
        try:
            reports = Report.objects.all().order_by('-create_time')
            report_list = [report.get_info() for report in reports]
            result = {'status':'200', 'message':'获取成功', 'content':report_list}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message': '', 'content':'none'}

        print(result)
        return JsonResponse(result, safe=False)
           
@admin_authentication
def get_trade_records(request):
    if request.method == 'GET':
        try:
            records = TradeRecord.objects.all()
            record_list = [record.get_info() for record in records]
            result = {'status':'200', 'message':'获取成功', 'content':record_list}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message': '', 'content':'none'}

        print(result)
        return JsonResponse(result, safe=False)

@csrf_exempt
@admin_authentication
def update_cash_status(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            trade_id = data.get('trade_id')
            trade_status = data.get('trade_status')
            record = TradeRecord.objects.get(id=trade_id)
            record.trade_status = trade_status
            record.save()
            
            result = {'status':'200', 'message':'更改成功', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message': '', 'content':'none'}

        print(result)
        return JsonResponse(result, safe=False)
 
@csrf_exempt
@admin_authentication
def add_recommand(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            item_id = data.get('item_id')
            if item_id:
                try:
                    item = ItemInfo.objects.get(id=item_id)
                    status = item.add_recommand()
                    if status == '1':
                        result = {'status':'200', 'message':'添加推荐成功', 'content':'none'}
                    elif status == '0':
                        result = {'status':'400', 'message':'项目未审核，不能添加推荐', 'content':'none'}
                    elif status == '2':
                        result = {'status':'400', 'message':'项目审核未通过，不能添加推荐', 'content':'none'}
                    else:
                        result = {'status':'400', 'message':'项目已结束，不能添加推荐', 'content':'none'}

                except:
                    log_exception()
                    result = {'status':'400', 'message':'项目不存在', 'content':'none'}
            else:
                result = {'status':'400', 'message':'未传入item_id', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False) 

@csrf_exempt
@admin_authentication
def cancel_recommand(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            item_id = data.get('item_id')
            if item_id:
                try:
                    item = ItemInfo.objects.get(id=item_id)
                    item.cancel_recommand()
                    result = {'status':'200', 'message':'取消推荐成功', 'content':'none'}
                except:
                    log_exception()
                    result = {'status':'400', 'message':'项目不存在', 'content':'none'}
            else:
                result = {'status':'400', 'message':'未传入item_id', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        return JsonResponse(result, safe=False) 


