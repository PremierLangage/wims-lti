from django.contrib import admin
from django.urls import path

from lti_app.views import toWims


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', toWims)
]
