from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RegisterSerializer
from rest_framework.permissions import IsAuthenticated

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=201)
        return Response(serializer.errors, status=400)

class UserTypeProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_type = request.user.user_type
        return Response({'user_type': user_type}, status=200)
  
