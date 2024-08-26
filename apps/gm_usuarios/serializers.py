from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

from .models import Usuario


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # @classmethod
    # def get_token(cls, user):
    #     token = super().get_token(user)

    #     return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Obtener el usuario asociado al token
        user = self.user

        # Incluir los datos del usuario en la respuesta        
        # data['username'] = user.username
        data['email'] = user.email
        data['full_name'] = user.get_full_name
        
        # Agregar la URL de la imagen
        if user.foto_perfil:
            data['foto_perfil'] = self.context['request'].build_absolute_uri(user.foto_perfil.url)
        else:
            data['foto_perfil'] = None

        # Puedes agregar más datos según sea necesario

        return data
    
class UsuarioSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False)
    
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'apellido_paterno', 'apellido_materno', 'nombres', 'full_name', 'image']
        read_only_fields = ['id', 'username']
        # extra_kwargs = {
        #     'nombres': {'required': True},
        #     'ape_paterno': {'required': True},
        #     'email': {'required': True},
        # }
        
    def get_full_name(self, obj):
        return obj.get_full_name()

    def create(self, validated_data):
        logger.info(f"Creando usuario con datos: {validated_data}")
        user = Usuario(**validated_data)
        user.save()
        logger.info(f"Usuario creado: {user.get_full_name}")
        return user

    # def send_activation_email(self, user):
    #     activation_link = f"{settings.SITE_URL}/activate/{user.activation_token}/"
    #     subject = "Activa tu cuenta"
    #     message = f"Hola {user.get_full_name()},\n\nPor favor, activa tu cuenta y establece tu contraseña haciendo clic en el siguiente enlace:\n\n{activation_link}\n\nGracias,\nEl equipo de soporte"
    #     send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        
    def update(self, instance, validated_data):
        image = validated_data.pop('image', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if image:
            # Eliminar la imagen anterior si existe
            if instance.image:
                instance.image.delete(save=False)
            # Guardar la nueva imagen
            instance.image.save(f"{instance.id}.{image.name.split('.')[-1]}", image, save=False)

        instance.save()
        return instance