import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import EmailValidator
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings

class UsuarioManager(BaseUserManager):
    def create_user(self, email, dni, nombres, apellido_paterno, apellido_materno, **extra_fields):
        if not email:
            raise ValueError('El Email institucional es obligatorio')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            dni=dni,
            nombres=nombres,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            **extra_fields
        )
        
        # Lógica para establecer is_active
        if extra_fields.get('is_superuser'):
            user.is_active=True
        else:
            user.is_active = False  # El usuario no está activo hasta que establezca su contraseña
        user.save(using=self._db)
        return user

    def create_superuser(self, email, dni, nombres, apellido_paterno, apellido_materno, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        
        user = self.create_user(email, dni, nombres, apellido_paterno, apellido_materno, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        _("Email institucional"),
        unique=True,
        validators=[EmailValidator(message=_("Ingrese un email institucional válido."))]
    )
    dni = models.CharField(_("DNI"), max_length=20, unique=True)
    nombres = models.CharField(_("Nombres"), max_length=150)
    apellido_paterno = models.CharField(_("Apellido paterno"), max_length=50)
    apellido_materno = models.CharField(_("Apellido materno"), max_length=50)
    
    # cargo = models.CharField(_("Cargo"), max_length=100)
    # departamento = models.CharField(_("Departamento"), max_length=100)
    # telefono = models.CharField(_("Teléfono"), max_length=20, blank=True)
    # direccion = models.CharField(_("Dirección"), max_length=255, blank=True)
    # fecha_nacimiento = models.DateField(_("Fecha de nacimiento"), null=True, blank=True)
    foto_perfil = models.ImageField(_("Foto de perfil"), upload_to='perfiles/', null=True, blank=True)
    
    is_active = models.BooleanField(_("Activo"), default=False)
    is_staff = models.BooleanField(_("Es staff"), default=False)
    date_joined = models.DateTimeField(_("Fecha de registro"), default=timezone.now)
    ultimo_acceso = models.DateTimeField(_("Último acceso"), null=True, blank=True)
    
    # es_funcionario = models.BooleanField(_("Es funcionario"), default=True)
    # nivel_acceso = models.IntegerField(_("Nivel de acceso"), default=1)
    # estado = models.CharField(_("Estado"), max_length=20, choices=[
    #     ('pendiente', 'Pendiente de activación'),
    #     ('activo', 'Activo'),
    #     ('inactivo', 'Inactivo'),
    #     ('suspendido', 'Suspendido')
    # ], default='pendiente')

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['dni', 'nombres', 'apellido_paterno', 'apellido_materno']

    class Meta:
        verbose_name = _("usuario")
        verbose_name_plural = _("usuarios")

    def __str__(self):
        return f"{self.nombre_completo} ({self.email})"

    @property
    def nombre_completo(self):
        return f"{self.apellido_paterno} {self.apellido_materno}, {self.nombres} "

    # def get_departamento_display(self):
    #     return self.departamento

    def desactivar_usuario(self):
        # self.estado = 'suspendido'
        self.is_active = False
        self.save()

    def activar_usuario(self):
        # self.estado = 'activo'
        self.is_active = True
        self.save()

    def save(self, *args, **kwargs):
        site_url = settings.SITE_URL
        print(f"email {site_url}")
        if not self.email.endswith(f'@{site_url}'):  # Ajusta esto al dominio de tu municipalidad
            raise ValueError("El email debe ser un correo institucional válido.")
        is_new = self.pk is None
        
        self.apellido_paterno = self.apellido_paterno.upper()
        self.apellido_materno = self.apellido_materno.upper()
        self.nombres = self.nombres.upper()
        
        super().save(*args, **kwargs)
        if is_new:
            self.enviar_correo_activacion()

    def enviar_correo_activacion(self):
        print("Enviando correo")
        # token = default_token_generator.make_token(self)
        # uid = urlsafe_base64_encode(force_bytes(self.pk))
        # activation_link = f"{settings.SITE_URL}/activar-cuenta/{uid}/{token}/"
        # subject = 'Activa tu cuenta en el Sistema de Gestión Municipal'
        # message = f"""
        # Hola {self.nombre_completo},

        # Se ha creado una cuenta para ti en el Sistema de Gestión Municipal. 
        # Para activar tu cuenta y establecer tu contraseña, por favor haz clic en el siguiente enlace:

        # {activation_link}

        # Este enlace es válido por 24 horas.

        # Si no has solicitado esta cuenta, por favor ignora este mensaje.

        # Saludos,
        # El equipo de Sistemas
        # """
        # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])