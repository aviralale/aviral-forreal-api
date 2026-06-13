from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .admin_api import AdminCategoryViewSet, AdminPostViewSet, AdminTagViewSet
from .auth import AdminLogin, AdminLogout
from .views import CategoryViewSet, PostViewSet, TagViewSet

router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')
router.register('categories', CategoryViewSet, basename='category')
router.register('tags', TagViewSet, basename='tag')

admin_router = DefaultRouter()
admin_router.register('posts', AdminPostViewSet, basename='admin-post')
admin_router.register('categories', AdminCategoryViewSet, basename='admin-category')
admin_router.register('tags', AdminTagViewSet, basename='admin-tag')

urlpatterns = router.urls + [
    path('admin/', include(admin_router.urls)),
    path('auth/login/', AdminLogin.as_view(), name='admin-login'),
    path('auth/logout/', AdminLogout.as_view(), name='admin-logout'),
]
