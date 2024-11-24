from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound, AuthenticationFailed
from authentication.models import User, UserRole
from authentication.serializers import UserRoleSerializer, UserSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(methods=['POST'], detail=False, url_path='register')
    def register(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = User.objects.get(email=request.data['email'])

        refresh = RefreshToken.for_user(user)
        response = Response()

        data = self.serializer_class(user).data

        response.data = {'access': str(refresh.access_token), 'data': data}
        return response
    
    @action(methods=['POST'], detail=False, url_path='login')
    def login(self, request):
        if 'email' not in request.data:
            raise ValidationError({'error': 'Please enter your email!'})
        if 'password' not in request.data:
            raise ValidationError({'error': 'Please enter your password!'})
        
        try:
            user = User.objects.get(email=request.data['email'])
        except User.DoesNotExist:
            raise NotFound({'error': 'The user with this email was not found. Please enter a valid email!'})

        if not user.check_password(request.data['password']):
            raise AuthenticationFailed({'error': 'This password is not correct. Check the login and enter the password again!'})

        refresh = RefreshToken.for_user(user)
        response = Response()

        data = self.serializer_class(user).data

        response.data = {'access': str(refresh.access_token), 'data': data}
        return response

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated], url_path='me')
    def get_user(self,request):
        user = request.user
        data = self.serializer_class(user).data
        return Response(data)



class UserRoleViewSet(ModelViewSet):
    serializer_class = UserRoleSerializer
    queryset = UserRole.objects.all()