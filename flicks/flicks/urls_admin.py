from django.contrib import admin
from django.conf import settings
from django.conf.urls import (
    url,
    static,
    include,
)

urlpatterns = [
    url(r'', admin.site.urls),
]
