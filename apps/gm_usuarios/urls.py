from django.urls import path
from .views import (LoginView, LogoutView)


urlpatterns = [
    path('api/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
]