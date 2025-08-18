# urls.py
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path("login/", LoginAPIView.as_view(), name="login"),
    path('', include(router.urls)),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh token

]
