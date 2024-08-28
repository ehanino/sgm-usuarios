from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from ...models import Usuario
from .serializers import CustomTokenObtainPairSerializer, UsuarioSerializer


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.context['request'] = request  # Añadir el request al contexto
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    
class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            user = get_object_or_404(Usuario, id=id)
            serializer = UsuarioSerializer(user)
            return Response(serializer.data)
        else:
            users = Usuario.objects.all()
            serializer = UsuarioSerializer(users, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        user = get_object_or_404(Usuario, id=id)
        serializer = UsuarioSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id):
        user = get_object_or_404(Usuario, id=id)
        serializer = UsuarioSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        user = get_object_or_404(Usuario, id=id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)