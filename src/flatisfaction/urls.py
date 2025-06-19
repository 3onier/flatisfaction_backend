from django.urls import path, include


from .users.views import UserProfileDetail, UserDetail, ChangePasswordView

urlpatterns = [
    path(r'auth/', include('knox.urls')),
    path(r'profile/', UserProfileDetail.as_view()),
    path(r'user/', UserDetail.as_view()),
    path(r'change-password/', ChangePasswordView.as_view()),
]
