from django.urls import include, path

from rest_framework.routers import DefaultRouter

from api import views
from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, TitleViewSet, UsersViewSet)

router_v1 = DefaultRouter()
router_v1.register('titles', TitleViewSet)
router_v1.register('categories', CategoryViewSet)
router_v1.register('genres', GenreViewSet)
router_v1.register('users', UsersViewSet, basename='get-users-v1')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews-title'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments-review'
)

urlpatterns = [
    path('v1/', include([
        path('auth/signup/', views.register_user, name='register'),
        path('auth/token/', views.token_obtain, name='token_obtain'),
        path('users/me/', views.change_profile, name='change_profile')
    ])),
    path('v1/', include(router_v1.urls)),
]
