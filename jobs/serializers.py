from rest_framework import serializers
from .models import User, JobSeeker, Employer

class RegisterSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = User
        fields = ['password', 'email', 'first_name', 'last_name', 'company_name', 'user_type']
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
        }

    def validate(self, data):
        user_type = data.get('user_type')

        if user_type == 'jobseeker':
            if not data.get('first_name'):
                raise serializers.ValidationError("Please enter first name")
            if not data.get('last_name'):
                raise serializers.ValidationError("Please enter last name")
            if not data.get('email'):
                raise serializers.ValidationError("Please enter email")
            if not data.get('password'):
                raise serializers.ValidationError("Please enter password")


        if user_type == 'employer':
            if not data.get('company_name'):
                raise serializers.ValidationError("Please enter a company name")
            if not data.get('email'):
                raise serializers.ValidationError("Please enter email")
            if not data.get('password'):
                raise serializers.ValidationError("Please enter password")

        return data

    def create(self, validated_data):
        user_type = validated_data.get('user_type')

        company_name = validated_data.pop('company_name', None)
        
        
        user = User.objects.create_user(
            username=validated_data['email'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            user_type=user_type
        )

        if user_type == 'jobseeker':
            JobSeeker.objects.create(user=user)
        elif user_type == 'employer':
            Employer.objects.create(user=user, company_name=company_name)

        return user
