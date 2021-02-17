from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login as django_login,
    logout as django_logout,
)
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.throttling import (
    AnonRateThrottle,
    UserRateThrottle,
)
from rest_framework import (
    authentication,
    permissions,
    viewsets,
    mixins
)
from .models import (
    Order,
    Rental
)
from .serializers import (
    OrderSerializer,
    RentalSerializer,
    UserSerializer
)

UserModel = get_user_model()


def get_or_create_user(username, password):
    created = False
    try:
        user = UserModel.objects.get(username=username)
    except:
        user = UserModel.objects.create(
            username=username,
        )
        if not password:
            user.set_unusable_password()
        else:
            user.set_password(password)
            user.is_active = True
        user.save()
        created = True

    return (user, created)


def get_or_create_token(user):
    token = Token.objects.filter(user=user)
    if token:
        return token.first()
    else:
        return Token.objects.create(user=user)


def destroy_token(user):
    user.auth_token.delete()


class UserCreateView(APIView):
    throttle_classes = (AnonRateThrottle,)
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            username = request.data.get("username")
            password = request.data.get("password")

            user, created = get_or_create_user(username, password)
            if not created:
                return Response({"message": "User already exists"},
                                status=HTTP_409_CONFLICT)

            token = get_or_create_token(user=user)
            return Response({"message": "Welcome", "token": token.key},
                            status=status.HTTP_201_CREATED)

        return Response({"message": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    throttle_classes = (AnonRateThrottle,)
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format='json'):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            return Response({"message": "Login failed"},
                            status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"message": "User not enabled"},
                            status=status.HTTP_403_FORBIDDEN)

        django_login(request, user)
        token = get_or_create_token(user)
        return Response({"message": "Welcome", "token": token.key})


class UserLogoutView(APIView):
    throttle_classes = (UserRateThrottle,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format='json'):
        try:
            destroy_token(request.user)
        except (AtributeError, ObjectDoesNotExists):
            pass

        django_logout(request)
        return Response({"message": "Thank you, Come again."},
                        status=status.HTTP_202_ACCEPTED)


class OrderViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    throttle_classes = (UserRateThrottle,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Order.objects.available()
    serializer_class = OrderSerializer

    def list(self, request):
        queryset = self.get_queryset().filter(
            lessee=request.user
        )
        serializer = self.serializer_class(
            queryset,
            many=True,
            context={'request': request}
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)

    def post(self, request, format='json'):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"message": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None, format='json'):
        if request.user.is_staff:
            queryset = self.get_queryset()
            obj = get_object_or_404(queryset, pk=pk)
            obj.is_deleted = True
            obj.save()
            return Response({"message": "Gone with the wind"},
                            status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "Nothing to see here"},
                            status=status.HTTP_403_FORBIDDEN)


class RentalViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    throttle_classes = (UserRateThrottle,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Rental.objects.available()
    serializer_class = RentalSerializer

    def list(self, request):
        queryset = self.get_queryset().filter(
            order__lessee=request.user
        )
        serializer = self.serializer_class(
            queryset,
            many=True,
            context={'request': request}
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)

    def put(self, request, pk=None, format='json'):
        if request.user.is_staff:
            queryset = self.get_queryset()
            obj = get_object_or_404(queryset, pk=pk)
            serializer = self.serializer_class(obj, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"message": serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Nothing to see here"},
                            status=status.HTTP_403_FORBIDDEN)
