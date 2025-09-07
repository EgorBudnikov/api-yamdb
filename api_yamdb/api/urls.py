from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api import views
from api.views import UsersViewSet

router_v1 = DefaultRouter()
router_v1.register('users', UsersViewSet, basename='get-users-v1')


urlpatterns = [
    path('v1/auth/signup/', views.register_user, name='register'),
    path('v1/auth/token/', views.token_obtain, name='token_obtain'),
    path('v1/users/me/', views.change_profile, name='change_profile'),
    path('v1/', include(router_v1.urls)),
]
