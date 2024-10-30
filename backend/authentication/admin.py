from django.contrib import admin
from authentication.models import User, UserRole

admin.site.register(User)
admin.site.register(UserRole)
# Register your models here.
