from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [
            "url",
            "username",
            "email",
            "subscribed_podcasts",
            "interested_podcasts",
        ]
        extra_kwargs = {
            "subscribed_podcasts": {"lookup_field": "slug"},
            "interested_podcasts": {"lookup_field": "slug"},
        }


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class UserView(RetrieveAPIView):
    serializer_class = UserSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user, context={"request": request})
        return Response(serializer.data)
