from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound, AuthenticationFailed
from authentication.models import User, UserRole, FriendRequest
from authentication.serializers import UserRoleSerializer, UserSerializer, FriendRequestSerializer
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
    
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def search(self, request):
        username = request.query_params.get('username', '')
        if not username:
            return Response(
                {'error': 'Параметр username обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        friend_ids = request.user.friends.values_list('id', flat=True)
        
        users = User.objects.filter(
            username__istartswith=username
        ).exclude(
            id=request.user.id
        ).exclude(
            id__in=friend_ids
        )
        
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def friends(self, request):
        """Получение списка друзей"""
        friends = request.user.friends.all()
        serializer = self.get_serializer(friends, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated], url_path='send-friend-request')
    def send_friend_request(self, request):
        """Отправка запроса в друзья"""
        username = request.data.get('username')
        if not username:
            return Response(
                {'error': 'Поле username обязательно'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            receiver = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if receiver == request.user:
            return Response(
                {'error': 'Нельзя отправить запрос самому себе'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем, не отправили ли уже запрос
        if FriendRequest.objects.filter(
            sender=request.user, 
            receiver=receiver,
            status=FriendRequest.PENDING
        ).exists():
            return Response(
                {'error': 'Вы уже отправили запрос этому пользователю'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем, не являются ли уже друзьями
        if request.user.friends.filter(id=receiver.id).exists():
            return Response(
                {'error': 'Этот пользователь уже у вас в друзьях'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        friend_request = FriendRequest.objects.create(
            sender=request.user,
            receiver=receiver
        )
        
        return Response(
            {
                'message': f'Запрос дружбы отправлен пользователю {username}',
                'request': FriendRequestSerializer(friend_request, context={'request': request}).data
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated], url_path='respond-friend-request')
    def respond_friend_request(self, request):
        """Ответ на запрос в друзья"""
        request_id = request.data.get('request_id')
        accept = request.data.get('accept', False)
        
        try:
            friend_request = FriendRequest.objects.get(
                id=request_id,
                receiver=request.user,
                status=FriendRequest.PENDING
            )
        except FriendRequest.DoesNotExist:
            return Response(
                {'error': 'Запрос не найден или уже обработан'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if accept:
            # Добавляем в друзья
            request.user.friends.add(friend_request.sender)
            friend_request.sender.friends.add(request.user)
            friend_request.status = FriendRequest.ACCEPTED
            message = 'Запрос дружбы принят'
        else:
            friend_request.status = FriendRequest.REJECTED
            message = 'Запрос дружбы отклонен'
        
        friend_request.save()
        
        return Response(
            {
                'message': message,
                'friends': UserSerializer(
                    request.user.friends.all(), 
                    many=True, 
                    context={'request': request}
                ).data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated], url_path='friend-requests')
    def friend_requests(self, request):
        """Получение списка входящих запросов в друзья"""
        requests = FriendRequest.objects.filter(
            receiver=request.user,
            status=FriendRequest.PENDING
        ).order_by('-created_at')
        
        serializer = FriendRequestSerializer(requests, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['PATCH'], permission_classes=[IsAuthenticated], url_path='update-profile')
    def update_profile(self, request):
        """Обновление профиля пользователя"""
        user = request.user
        photo = request.data.get('photo')
        role_id = request.data.get('role')
        
        if photo is not None:
            user.photo = photo
        
        if role_id is not None:
            try:
                role = UserRole.objects.get(id=role_id)
                user.role = role
            except UserRole.DoesNotExist:
                return Response(
                    {'error': 'Указанная роль не существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        user.save()
        
        return Response(
            UserSerializer(user, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    # Обновим существующий метод add_friend (можно оставить для обратной совместимости или удалить)
    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated], url_path='add-friend')
    def add_friend(self, request):
        """Совместимость со старым API, теперь использует систему запросов"""
        return self.send_friend_request(request)
    
    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated], url_path='remove-friend')
    def remove_friend(self, request):
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
        
        # Проверяем, есть ли пользователь в друзьях
        if not request.user.friends.filter(id=friend.id).exists():
            return Response(
                {'error': 'Этот пользователь не находится у вас в друзьях'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Удаляем из друзей
        request.user.friends.remove(friend)
        friend.friends.remove(request.user)
        
        # Получаем обновлённый список друзей
        current_friends = request.user.friends.all()
        
        return Response({
            'message': f'Пользователь {username} удалён из друзей',
            'friends': UserSerializer(current_friends, many=True, context={'request': request}).data
        }, status=status.HTTP_200_OK)



class UserRoleViewSet(ModelViewSet):
    serializer_class = UserRoleSerializer
    queryset = UserRole.objects.all()