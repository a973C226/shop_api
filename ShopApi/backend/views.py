from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.serializers import UserSerializer, ContactSerializer, CategorySerializer, ShopSerializer, ShopDetailsSerializer
from backend.models import Contact, Category, Shop

class RegisterAccount(APIView):

    def post(self, request, *args, **kwargs):

        if {'first_name', 'last_name', 'email', 'password', 'password_confirm', 'company', 'position'}.issubset(request.data):
            errors = {}

            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                request.data._mutable = True
                request.data.update({})
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    if request.data['password'] != request.data['password_confirm']:
                        return JsonResponse({'Status': False, 'Errors': 'The password and password confirmation must match.'})
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    if user.type == 'shop':
                        user.is_staff = True
                    user.save()
                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

        return JsonResponse({'Status': False,
                             'Errors': 'Не указаны все необходимые аргументы '
                                       '(first_name, last_name, email, password, password_confirm, company, position)'})


class LoginAccount(APIView):

    def post(self, request, *args, **kwargs):

        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])

            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)

                    return JsonResponse({'Status': True, 'Token': token.key})

            return JsonResponse({'Status': False, 'Errors': 'Не удалось авторизовать'})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы (email, password)'})


class ContactView(APIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        contact = Contact.objects.filter(
            user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if {'city', 'street', 'phone'}.issubset(request.data):
            request.data._mutable = True
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы (city, street, phone)'})

    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            query = Q()
            objects_deleted = False
            for contact_id in items_list:
                if contact_id.isdigit():
                    query = query | Q(user_id=request.user.id, id=contact_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = Contact.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if 'id' in request.data:
            if request.data['id'].isdigit():
                contact = Contact.objects.filter(id=request.data['id'], user_id=request.user.id).first()
                print(contact)
                if contact:
                    serializer = ContactSerializer(contact, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return JsonResponse({'Status': True})
                    else:
                        JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы (id)'})


class AccountDetails(APIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if 'password' in request.data:
            errors = {}

            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []

                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                request.user.set_password(request.data['password'])

        user_serializer = UserSerializer(request.user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': user_serializer.errors})


class CategoryView(ListAPIView):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):

    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class ShopAddView(APIView):

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        if not (request.user.is_staff and request.user.type == 'shop'):
            return JsonResponse({'Status': False, 'Error': "Staff status is false or type is not 'shop'"}, status=403)
        print(request.data)
        if {'name', 'state'}.issubset(request.data):
            request.data._mutable = True
            request.data.update({'user': request.user.id})
            print(request.data)
            serializer = ShopDetailsSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы (name, state)'})


class ShopDetailsView(APIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        if not (request.user.is_staff and request.user.type == 'shop'):
            return JsonResponse({'Status': False, 'Error': "Staff status is false or type is not 'shop'"}, status=403)

        try:
            shop = request.user.shop
            serializer = ShopDetailsSerializer(shop)
            return Response(serializer.data)
        except Exception as ex:
            return JsonResponse({'Status': False, 'Errors': ex.__str__()}, status=403)

    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        if not (request.user.is_staff and request.user.type == 'shop'):
            return JsonResponse({'Status': False, 'Error': "Staff status is false or type is not 'shop'"}, status=403)

        deleted_count = Shop.objects.filter(user_id=request.user.id).delete()[0]
        return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})


    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        if not (request.user.is_staff and request.user.type == 'shop'):
            return JsonResponse({'Status': False, 'Error': "Staff status is false or type is not 'shop'"}, status=403)

        shop = Shop.objects.filter(user_id=request.user.id).first()
        if shop:
            serializer = ShopDetailsSerializer(shop, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': serializer.errors})
        else:
            return JsonResponse({'Status': False, 'Errors': 'There are no registered shops'})


class PartnerState(APIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        if not (request.user.is_staff and request.user.type == 'shop'):
            return JsonResponse({'Status': False, 'Error': "Staff status is false or type is not 'shop'"}, status=403)

        try:
            shop = request.user.shop
            serializer = ShopSerializer(shop)
            return Response(serializer.data)
        except Exception as ex:
            return JsonResponse({'Status': False, 'Errors': ex.__str__()}, status=403)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        if not (request.user.is_staff and request.user.type == 'shop'):
            return JsonResponse({'Status': False, 'Error': "Staff status is false or type is not 'shop'"}, status=403)

        state = request.data.get('state')
        if state:
            try:
                if state.lower() == 'true':
                    state = True
                else:
                    state = False
                shop = Shop.objects.filter(user_id=request.user.id)
                if shop:
                    shop.update(state=state)
                else:
                    return JsonResponse({'Status': False, 'Errors': 'There are no registered shops'})
                return JsonResponse({'Status': True})
            except ValueError as error:
                return JsonResponse({'Status': False, 'Errors': str(error)})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})




