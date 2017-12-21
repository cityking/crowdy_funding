from crowdy_funding.project_content.models import ItemInfo
from crowdy_funding.personal_center.models import MyUser 
from config.tool import trade_url
import datetime
import requests
def test():
    print(123)

def tasks():
    items = ItemInfo.objects.filter(examination_status='1')
    for item in items:
        if item.left_time > 0:
            item.left_time -= 1
            item.save()
        else:
            url = trade_url + '/gateway/receipt'
            if item.funding_money < item.objective_money:

                data = {
                    'source':'crowdfunding', 
                    'source_id': '$%s$'%item.id,
                    'receipt_status': 'refund',
                }

                response = requests.put(url=url, json=data)
                response = response.json()
                if response['status'] == '200':
                    item.examination_status = '4'
                    item.funding_money = 0

                #else:
                #    print(response['message'])
                 
                #退款
            else:
                #打款 
                data = {
                    'source':'crowdfunding', 
                    'source_id': '$%s$'%item.id,
                    'receipt_status': 'confirm',
                }
                
                response = requests.put(url=url, json=data)
                response = response.json()
                if response['status'] == '200':
                    item.examination_status = '3'
 
            item.save()
def update_score():
    time = datetime.datetime.now()
    MyUser.objects.all().update(day_score=0)
    if time.day == 1:
        #更新月榜单
        MyUser.objects.all().update(month_score=0)
    if time.weekday() == 0:
        #更新周榜单
        MyUser.objects.all().update(week_score=0)

    

            


