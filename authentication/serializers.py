from rest_framework import serializers

from authentication.models import User


class UserSerializer(serializers.ModelSerializer):
    error_text = "Use Forms to create and update user"

    class Meta:
        model = User
        fields = ('name', 'email', 'phone_number', 'avatar', 'date_joined', 'is_active')

    def validate(self, attrs):
        raise serializers.ValidationError(self.error_text)
