from django.conf.urls import url

from tasks import views

app_name='tasks'

urlpatterns = [
    url(r'^options$', views.get_options)
]
