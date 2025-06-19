from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import authenticate

from .models import UserProfile
from .serializers import UserProfileSerializer, UserSerializer, PasswordChangeSerializer

# show own user profile
class UserProfileDetail(APIView):
    """
        Show and edit user profile
        It extends Djangos usermodel to also show customized fields as well
        Expects UserProfile Model

        User object will be determined by authetication
    """

    def get(self, request, format=None):
        try:
            user_profile = UserProfile.objects.get(
                user=request.user
            )
        except:
            # if no profile has been created just return an empty one
            user_profile = UserProfile()
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data) 
    
    def put(sefl, request, format=None):
        # TODO make userprofile picture work eventually. amt it can only be displayed
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserDetail(APIView):
    """
        Show and edit user
        Expects User model
    """
    def get(self, request, format=None):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request, format=None):
        serializer = UserSerializer(request.user, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

class ChangePasswordView(APIView):
    """
        Change the Password of logged in user

    Args:
        old_password
        new_password
    """
    def put(self, request, format=None):
        # check if user typed in the right old password
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid()
        
        if not request.user.check_password(serializer.data["old_password"]):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        user = request.user
        user.set_password(serializer.data["new_password"])
        user.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)