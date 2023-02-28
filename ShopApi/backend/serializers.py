from rest_framework import serializers
from backend.models import User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'middle_name', 'username', 'email', 'company', 'position')
        read_only_fields = ('id',)