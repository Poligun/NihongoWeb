from django.conf.urls import url
from nihongo.views import *

urlpatterns = [
    url(r'^$', NihongoView.as_view(), name = 'nihongo'),
    url(r'^api$', apiView, name = 'api'),
]
