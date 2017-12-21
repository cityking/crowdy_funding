from django.contrib import admin
from .models import *

admin.site.register(MyUser)
admin.site.register(Order)
admin.site.register(RedPacket)
admin.site.register(UserConsignee)
# Register your models here.
