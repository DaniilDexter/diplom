from rest_framework import serializers

from .models import User, UserRole


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):

    role = UserRoleSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'photo', 'role', 'created_at', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)
        instance.save()

        return instance