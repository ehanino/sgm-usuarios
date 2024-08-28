from django.urls import path
from .views import (LoginView, LogoutView, UserAPIView)


urlpatterns = [
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    path('usuarios/', UserAPIView.as_view(), name='listar-crear-usuario'),
    path('usuarios/<uuid:id>/', UserAPIView.as_view(), name='detalle-actualizar-eliminar-usuario'),
]