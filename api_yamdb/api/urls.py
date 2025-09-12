from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views


router_v1 = DefaultRouter()
router_v1.register('titles', views.TitleViewSet, basename='titles-v1')
router_v1.register('categories', views.CategoryViewSet,
                   basename='categories-v1')
router_v1.register('genres', views.GenreViewSet, basename='genres-v1')
router_v1.register('users', views.UsersViewSet, basename='get-users-v1')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    views.ReviewViewSet,
    basename='reviews-title-v1'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentViewSet,
    basename='comments-review-v1'
)

urlpatterns = [
    path('v1/', include([
        path('', include(router_v1.urls)),
        path('auth/', include(
            [
                path('signup/', views.register_user, name='register'),
                path('token/', views.token_obtain, name='token_obtain')
            ]
        )
        ),
    ])),
]
