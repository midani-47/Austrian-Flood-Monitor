from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from .models import WaterLevel, Account
from .serializers import WaterLevelSerializer, AccountSerializer




class AccountView(APIView):
    def get(self, request):
        accounts = Account.objects.all()
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ValidateEmailView(APIView):
    def get(self, request):
        email = request.query_params.get('email', None)
        if not email:
            return Response({"error": "Email parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        if Account.objects.filter(email=email).exists():
            return Response({"valid": True}, status=status.HTTP_200_OK)
        return Response({"valid": False}, status=status.HTTP_404_NOT_FOUND)


class ValidateUserView(APIView):
    def get(self, request):
        username = request.query_params.get('username', None)
        if not username:
            return Response({"error": "Username parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        if Account.objects.filter(username=username).exists():
            return Response({"valid": True}, status=status.HTTP_200_OK)
        return Response({"valid": False}, status=status.HTTP_404_NOT_FOUND)


class WaterLevelView(APIView):

    def get(self, request):
        water_levels = WaterLevel.objects.all()  # Retrieve all records
        serializer = WaterLevelSerializer(water_levels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = WaterLevelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)