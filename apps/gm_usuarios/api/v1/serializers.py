from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

from ...models import Usuario


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
        data['email'] = user.email
        data['full_name'] = user.get_full_name
        
        # Agregar la URL de la foto_perfiln
        if user.foto_perfil:
            data['foto_perfil'] = self.context['request'].build_absolute_uri(user.foto_perfil.url)
        else:
            data['foto_perfil'] = None

        # Puedes agregar más datos según sea necesario

        return data
    
class UsuarioSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    foto_perfil = serializers.ImageField(required=False)
    
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'dni', 'apellido_paterno', 'apellido_materno', 'nombres', 'full_name', 'foto_perfil','is_active']
        read_only_fields = ['id']
        # extra_kwargs = {
        #     'nombres': {'required': True},
        #     'ape_paterno': {'required': True},
        #     'email': {'required': True},
        # }
        
    def get_full_name(self, obj):
        return obj.get_full_name
    
    def validate_email(self, value):
        if self.instance and self.instance.email != value:
            raise serializers.ValidationError(_("No se puede cambiar el email de un usuario existente."))
        return value
    
    def validate_dni(self, value):
        print("Validando DNI:", value)
        if not value or value.strip() == '':
            raise serializers.ValidationError(_('El DNI es obligatorio y no puede estar vacío.'))
        return value

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
        foto_perfil = validated_data.pop('foto_perfil', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if foto_perfil:
            # Eliminar la foto_perfiln anterior si existe
            if instance.foto_perfil:
                instance.foto_perfil.delete(save=False)
            # Guardar la nueva foto_perfiln
            instance.foto_perfil.save(f"{instance.id}.{foto_perfil.name.split('.')[-1]}", foto_perfil, save=False)

        instance.save()
        return instance