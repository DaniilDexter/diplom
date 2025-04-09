from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound, AuthenticationFailed
from authentication.models import User, UserRole
from authentication.serializers import UserRoleSerializer, UserSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from rest_framework import status


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
    
    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def remove_friend(self, request):
        username = request.data.get('username')
        if not username:
            return Response({'error': 'Поле username обязательно'}, status=400)
        
        try:
            friend = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=404)
        
        request.user.friends.remove(friend)
        friend.friends.remove(request.user)
        
        return Response({'message': f'Пользователь {username} удален из друзей'})
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def search(self, request):
        username = request.query_params.get('username', '')
        if not username:
            return Response(
                {'error': 'Параметр username обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        users = User.objects.filter(
            username__istartswith=username
        ).exclude(id=request.user.id)
        
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def add_friend(self, request):
        username = request.data.get('username')
        if not username:
            return Response(
                {'error': 'Поле username обязательно'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            friend = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if friend == request.user:
            return Response(
                {'error': 'Нельзя добавить себя в друзья'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.user.friends.filter(id=friend.id).exists():
            return Response(
                {'error': 'Этот пользователь уже у вас в друзьях'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.user.friends.add(friend)
        friend.friends.add(request.user)
        
        return Response(
            {'message': f'Пользователь {username} добавлен в друзья'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def friends(self, request):
        """Получение списка друзей"""
        friends = request.user.friends.all()
        serializer = self.get_serializer(friends, many=True)
        return Response(serializer.data)



class UserRoleViewSet(ModelViewSet):
    serializer_class = UserRoleSerializer
    queryset = UserRole.objects.all()