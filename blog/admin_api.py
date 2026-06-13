from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser

from .admin_serializers import (
    CategoryAdminSerializer,
    PostAdminSerializer,
    TagAdminSerializer,
)
from .models import Category, Post, Tag


class AdminPostViewSet(viewsets.ModelViewSet):
    """Full CRUD over every post (drafts included). Staff only."""

    queryset = (
        Post.objects.all()
        .select_related('category')
        .prefetch_related('tags')
    )
    serializer_class = PostAdminSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['status']
    search_fields = ['title', 'excerpt', 'body']
    ordering_fields = ['created_at', 'published_at', 'title']
    ordering = ['-created_at']
    pagination_class = None


class AdminCategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategoryAdminSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None


class AdminTagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagAdminSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None
