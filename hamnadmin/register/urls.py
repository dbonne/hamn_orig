from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout, logout_then_login

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'hamnadmin.register.views.root'),
    (r'^new/$', 'hamnadmin.register.views.new'),
    (r'^discover/(\d+)/$', 'hamnadmin.register.views.discover'),
    (r'^delete/(\d+)/$', 'hamnadmin.register.views.delete'),

    (r'^log/(\d+)/$','hamnadmin.register.views.logview'),
    (r'^blogposts/(\d+)/$', 'hamnadmin.register.views.blogposts'),
    (r'^blogposts/(\d+)/hide/(\d+)/$', 'hamnadmin.register.views.blogpost_hide'),
    (r'^blogposts/(\d+)/unhide/(\d+)/$', 'hamnadmin.register.views.blogpost_unhide'),
    (r'^blogposts/(\d+)/delete/(\d+)/$', 'hamnadmin.register.views.blogpost_delete'),

    (r'^login/$', login),
    (r'^logout/$', logout_then_login, {'login_url':'/'}),

    (r'^admin/(.*)', admin.site.root),
)
