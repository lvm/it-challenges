from django.contrib import admin
from models import TwitterUser

class TwitterUserAdmin(admin.ModelAdmin):
    pass

admin.site.register(TwitterUser, TwitterUserAdmin)
