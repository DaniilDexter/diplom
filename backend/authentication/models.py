from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from authentication.manager import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='Email адрес', max_length=255, unique=True)
    username = models.CharField(verbose_name='Имя пользователя', max_length=255, unique=True)
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True, verbose_name="Фотография пользователя")
    role = models.ForeignKey('UserRole', on_delete=models.SET_NULL, null=True, default=2, verbose_name="Роль")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    friends = models.ManyToManyField('User', blank=True, verbose_name="Друзья")

    is_active = models.BooleanField(verbose_name='Активирован', default=True)
    is_staff = models.BooleanField(verbose_name='Сотрудник', default=False)
    is_superuser = models.BooleanField(verbose_name='Администратор', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class UserRole(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название роли")
    description = models.TextField(blank=True, null=True, verbose_name="Описание роли")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Роль пользователя"
        verbose_name_plural = "Роли пользователей"


class FriendRequest(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (PENDING, 'Ожидает'),
        (ACCEPTED, 'Принят'),
        (REJECTED, 'Отклонен'),
    ]
    
    sender = models.ForeignKey(
        User, 
        related_name='sent_friend_requests', 
        on_delete=models.CASCADE,
        verbose_name="Отправитель"
    )
    receiver = models.ForeignKey(
        User, 
        related_name='received_friend_requests', 
        on_delete=models.CASCADE,
        verbose_name="Получатель"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES,
        default=PENDING,
        verbose_name="Статус"
    )

    class Meta:
        verbose_name = "Запрос в друзья"
        verbose_name_plural = "Запросы в друзья"
        constraints = [
            models.UniqueConstraint(
                fields=['sender', 'receiver'], 
                name='unique_friend_request',
                condition=models.Q(status='pending')
            )
        ]

    def __str__(self):
        return f"{self.sender} → {self.receiver} ({self.status})"
