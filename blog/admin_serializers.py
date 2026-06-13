from rest_framework import serializers
from .models import Post, Category, Tag


class CategoryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']
        extra_kwargs = {'slug': {'required': False}}


class TagAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        extra_kwargs = {'slug': {'required': False}}


class PostAdminSerializer(serializers.ModelSerializer):
    """Read + write representation for the dashboard. category/tags are handled
    by primary key; cover_image accepts a file on write and returns an absolute
    URL on read (DRF resolves it from the request in the serializer context)."""

    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), allow_null=True, required=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=False
    )

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'body', 'cover_image',
            'category', 'tags', 'status', 'published_at',
            'reading_time', 'views', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'reading_time', 'views', 'published_at', 'created_at', 'updated_at',
        ]
        extra_kwargs = {'slug': {'required': False}}
