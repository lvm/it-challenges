from rest_framework import serializers
from models import TwitterUser

class TwitterUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TwitterUser
        fields = ('username','followers','description','avatar')
