from rest_framework import serializers
from backend.models import User, Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'user', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }


class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id',
                  'first_name',
                  'last_name',
                  'middle_name',
                  'username',
                  'email',
                  'company',
                  'position',
                  'type',
                  'is_staff',
                  'is_superuser')
        read_only_fields = ('id',)