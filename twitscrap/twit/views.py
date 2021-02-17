from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from models import TwitterUser
from serializers import TwitterUserSerializer
from tasks import import_user


@api_view(['GET'])
def list_users(request, username=None):
    # if there's an user, give me its info
    # else, give me all of them (beware: not paginated).
    if username:
        user = get_object_or_404(TwitterUser, username=username)
        serializer = TwitterUserSerializer(user)
    else:
        users = TwitterUser.objects.all()
        serializer = TwitterUserSerializer(users, many=True)

    return Response(serializer.data)


@api_view(['POST'])
def add_user(request, username):
    # if there's an user, try to create a new one
    # else, nothing can be done.
    if username:
        # run the task to create the user
        # (see: tasks.py for more info about the process of creation)
        import_user(username)
        return Response({'status': 'ok', 'message': 'processing request'})
    else:
        return Response({'status': 'err', 'message': 'missing username'})


@api_view(['GET', 'POST'])
def users(request, username):
    # depending on the request, send the petition to
    # any of the methods
    if request.method == 'GET':
        return list_users(request, username)
    elif request.method == 'POST':
        return add_user(request, username)
    else:
        return Response({})
