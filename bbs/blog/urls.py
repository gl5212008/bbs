from django.conf.urls import url
from blog import views

urlpatterns = [
    url(r'^backend/$', views.backend),
    url(r'^add_article/$', views.add_article),
    url(r'^upload/$', views.upload),

    url(r'^(\w+)/$', views.home),

    # url(r'^(\w+)/category/(\w+)/$', views.category),
    # url(r'^(\w+)/tag/(\w+)/$', views.tag),
    # url(r'^(\w+)/archive/(\w+)/$', views.archive),


    # 优化第一版
    # url(r'^(\w+)/(category|tag|archive)/(\w+)/$', views.threeinone),


    # 优化第二版
    url(r'^(\w+)/(category|tag|archive)/(.*)/$', views.home),  # home(request, username, category, xx)

    # day80


    # --------- day78 ↓ ----------------------
    url(r'^(\w+)/p/(\d+)', views.article),
]