from django.urls import path
from .views import (LoginView, LogoutView, UserAPIView)


urlpatterns = [
    path('v1/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('v1/logout/', LogoutView.as_view(), name='logout'),
    
    path('v1/usuarios/', UserAPIView.as_view(), name='listar-crear-usuario'),
    path('v1/usuarios/<uuid:id>/', UserAPIView.as_view(), name='detalle-actualizar-eliminar-usuario'),
]