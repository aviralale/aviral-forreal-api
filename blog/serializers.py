from rest_framework import serializers
from .models import Post, Category, Tag


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class PostListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    cover_image = serializers.SerializerMethodField()

    def get_cover_image(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.cover_image.url) if request else obj.cover_image.url
        return None

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'cover_image',
            'category', 'tags', 'published_at', 'reading_time', 'views'
        ]


class PostDetailSerializer(PostListSerializer):
    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ['body']
