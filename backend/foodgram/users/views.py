from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import LimitPagination
from .serializers import FollowSerializer
from .models import Follow

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    pagination_class = LimitPagination

    @action(detail=True, permission_classes=[IsAuthenticated],
            methods=['post', 'delete'])
    def subscribe(self, request, id=None):
        """Подписаться на человека."""
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if Follow.objects.filter(user=request.user,
                                     author=author).exists():
                return Response({
                    'errors': 'Вы подписаны на данного пользователя'
                }, status=status.HTTP_400_BAD_REQUEST)
            follow = Follow.objects.create(user=request.user, author=author)
            serializer = FollowSerializer(
                follow, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            follow = get_object_or_404(
                Follow, user=request.user, author=author)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Подписки."""
        queryset = Follow.objects.filter(user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
