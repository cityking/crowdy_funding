from django.shortcuts import render
from crowdy_funding.project_content.models import ItemInfo, UserPayBack
from django.http import JsonResponse,HttpResponse
from urllib.parse import urljoin
import json
import traceback
# Create your views here.

from django.views.decorators.csrf import csrf_exempt
from .models import ItemInfo, get_user_item, ItemType, Comment
from config.tool import * 
from crowdy_funding.personal_center.models import MyUser, Order
from crowdy_funding.personal_center.views import register
from admin_project.models import Carousel


@csrf_exempt
@authentication
def item_initiate(request):
    if request.method == 'POST':
        try: 
            data = request.POST.dict()

            identity = data.get('identity')

            try: 
                images = []
                files = request.FILES.getlist('img')
                bucket_domain = 'http://cdn.hopyun.com/'
                if files:
                    for image in files:
                        url = upload_file(image.file.read(), name=image.name)
                        url = urljoin(bucket_domain, url)
                        images.append(url)
                data['media_url'] = str(images)
            except Exception as e:
                result = {'status':'400', 'message':'上传图片失败 %s' % str(e), 'content':'none'}
                return JsonResponse(result, safe=False) 
            
            user = MyUser.get_user_by_identity(identity)

            items = ItemInfo.objects.filter(initiator=user).exclude(examination_status='3').exclude(examination_status='4').exclude(examination_status='2')
            if items:
                result = {'status':'400', 'message':'该用户已发起过项目', 'content':'none'}
                return JsonResponse(result, safe=False) 
            item = ItemInfo.create(data, user)
            if item:
                result = {'status':'200', 'message':'项目发起成功', 'content':'none'} 
            else:
                result = {'status':'400', 'message':'项目发起失败', 'content':'none'}
        except Exception as e:
            print(e)
            result = {'status':'400', 'message':'项目发起失败', 'content':'none'}
        print(result) 
        return JsonResponse(result, safe=False) 
@csrf_exempt
@authentication
def item_update(request):
    if request.method == 'POST':
        try:
            data = request.POST.dict()
            item_id = request.POST.get('item_id')
            item = ItemInfo.objects.get(id=item_id)

            images = request.POST.get('ori_img')
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
            data['examination_status'] = '0'

            item = item.update(data)
            if not item:
                result = {'status':'400', 'message':'更新失败', 'content':'none'}
            else:
                result = {'status':'200', 'message':'success', 'content':'none'}
        except Exception as e:
            print(e)
            result = {'status':'400', 'message':'fail', 'content':'none'}

        print(result)
        return JsonResponse(result, safe=False)
    else:
        response = JsonResponse(None, safe=False)
        return response


@authentication
def item_detail(request):
    if request.method == 'GET':
        try:
            item_id = request.GET.get('item_id')
            item = ItemInfo.objects.get(pk=item_id)
            identity = request.GET.get('identity')
            try:
                #user = MyUser.objects.get(openid=identity)
                user = MyUser.get_user_by_identity(identity)
            except Exception as e:
                result = {'status':'400', 'message':'获取用户失败 %s' % str(e), 'content':'none'} 
                return JsonResponse(result, safe=False)

            details = item.get_item_detail(user)

            
            if user in item.collect_users.all():
                collected = 1
            else: collected = 0

            details['collected'] = collected

            
            result = {'status':'200', 'message':'success', 'content':details} 
        except Exception as e:
            result = {'status':'400', 'message':'fail %s' % str(e), 'content':'none'} 
        print(result)
        return JsonResponse(result, safe=False)

@authentication
def item_management(request):
    if request.method == 'GET':
        try:
            identity = request.GET.get('identity')
            item_id = request.GET.get('item_id')
            try:
                item = ItemInfo.objects.get(id=item_id)
            except:
                result = {'status':'400', 'message':'项目不存在', 'content':'none'} 
                return JsonResponse(result, safe=False)
                
            if item:
                manage_info = item.get_manage_info()
                result = {'status':'200', 'message':'success', 'content':manage_info} 
            else:
                result = {'status':'400', 'message':'项目不存在', 'content':'none'} 
        except Exception as e:
            result = {'status':'400', 'message':str(e), 'content':'none'} 
        print(result)
        return JsonResponse(result, safe=False)

@authentication
def get_payback_detail(request):
    if request.method == 'GET': 
        paback_id = request.GET.get('payback_id') 
        try:
            payback = UserPayBack.objects.get(pk=paback_id)
            info = payback.get_info()
            result = {'status':'200', 'message':'success', 'content':info} 
        except Exception as e:
            result = {'status':'400', 'message': str(e), 'content':'none'}
        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def payback_commit(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            payback_id = data.get('payback_id')
            payback = UserPayBack.objects.get(id=payback_id)
            delivery_company = data.get('delivery_company')
            delivery_id = data.get('delivery_id')
            content = data.get('content')
            payback.delivery_company = delivery_company
            payback.delivery_id = delivery_id
            payback.content = content
            payback.order.delivery_status = '2'
            payback.status = '1'
            
            payback.save()

            result = {'status':'200', 'message':'回报成功', 'content':'none'}
        except Exception as e:
            result = {'status':'400', 'message': str(e), 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)
def get_item_comments(request):
    if request.method == 'GET':
        item_id = request.GET.get('item_id')
        item = ItemInfo.objects.get(pk=item_id)
        comments = Comment.get_item_comments(item)
        result = {'status':'200', 'message':'success', 'content':comments} 
        return JsonResponse(result, safe=False)
        
@pagination
def index(request):
    if request.method == 'GET':
        try:
            data = request.GET
            page_no = data.get('page_no')
            page_count = data.get('page_count')
            if not page_no:
                page_no = 1
            if not page_count:
                page_count = 10
            items = ItemInfo.objects.all().filter(examination_status='1').filter(recommand='1')
            item_list = []
            for item in items:
                item_list.append(item.get_item_dict())
            
            result = {'status':'200', 'message':'success', 'content':item_list, 'length':len(item_list)}
        except Exception as e:
            print(e)
            result = {'status':'400', 'message':'fail %s' % str(e), 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)

def get_item_type(request):
    if request.method == 'GET':
        try:
            types = ItemType.objects.all()
            type_list = [t.get_dict() for t in types]
            result = {'status':'200', 'message':'success', 'content':type_list}
        except Exception as e:
            result = {'status':'400', 'message':'fail %s' % str(e), 'content':'none'}
        return JsonResponse(result, safe=False)
        
def filter_items(request):
    if request.method == 'GET':
        try:
            page_no = request.GET.get('page_no')
            page_count = request.GET.get('page_count')
            type_id = request.GET.get('type_id')
            time_sort = request.GET.get('time_sort')
            support_sort = request.GET.get('support_sort')
        
            if not type_id:
                items = ItemInfo.objects.all().filter(examination_status='1')
            else:
                item_type = ItemType.objects.get(id=type_id)
                items = ItemInfo.objects.all().filter(examination_status='1').filter(item_type=item_type)

            #排序
            if time_sort == "timeA":
                items = items.order_by('create_time')
            elif time_sort == 'timeD':
                items = items.order_by('-create_time')

            item_list = []
            for item in items:
                item_list.append(item.get_item_dict())

            if support_sort == 'supportA':
                item_list.sort(key = lambda x : x['schedule'])
            elif support_sort == 'supportD':
                item_list.sort(key = lambda x : x['schedule'], reverse=True)

            length = len(item_list)
            if not page_no:
                page_no = 1
            else:
                page_no = int(page_no)
            if not page_count:
                page_count = 5
            else:
                page_count = int(page_count)

            pages = length/page_count
            if length % page_count:
                pages += 1
           
            start = (page_no-1)*page_count
            if page_no == int(pages):
                end = length 
            else:
                end = page_no*page_count

            item_list = item_list[start:end]
        
            
            
            result = {'status':'200', 'message':'success', 'content':item_list, 'length':length}
        except Exception as e:
            print(e)
            result = {'status':'400', 'message':'fail %s' % str(e), 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)



def operate(request):
    if request.method == 'GET':
        try:
            item_id = request.GET.get('item_id')
            item = ItemInfo.objects.get(id=item_id)
            
            operation = request.GET.get('operation')
            if operation == '0':
                #取消
                item.examination_status = '2'
                item.recommand = '0'
                
            elif operation == '1':
                #审核通过
                item.examination_status = '1'
            elif operation == '2':
                #推荐
                if item.recommand == '0' and item.examination_status == '1':
                    item.recommand = '1'
                else:
                    item.recommand = '0'

            elif operation == '3':
                item.examination_status = '4'
                item.recommand = '0'
                
            else:
                result = {'status':'400', 'message':'请传入正确的参数operation', 'content':'none'} 
                return JsonResponse(result, safe=False)
            item.save()
            result = {'status':'200', 'message':'success', 'content':'none'} 
        except Exception as e:
            print(e)
            result = {'status':'400', 'message':'fail', 'content':'none'} 


        return JsonResponse(result, safe=False)
    else:
        response = JsonResponse(None, safe=False)
        return response 
       


def get_carousel(request):
    if request.method == 'GET':
        try:
            carousel_list = Carousel.objects.all()
            carousel_list = [carousel.get_info() for carousel in carousel_list]
            result = {'status':'200', 'message':'获取成功', 'content':carousel_list}

        except Exception as e:
            result = {'status':'400', 'message':str(e), 'content':'none'}
        return JsonResponse(result, safe=False)



