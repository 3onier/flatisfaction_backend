from django.urls import path, include


from .users.views import UserProfileDetail, UserDetail, ChangePasswordView

from .flat.views import FlatView, FlatsView, FlatMembersView, FlatMemberView ,FlatAdminsView, FlatAdminView, MakeAdminView, LeaveFlat
from .invite.views import OpenInviteView, ListAndCreateInviteView, PublicInviteView, RetrieveDestroyInvite
from .chore.views import ListAllUserChores, RetrieveUpdateDestroyChore, ListCreateFlatChores, ListChoreAppointments, ScheduleCreateDeleteView, RetrieveUpdateDestroyChoreAppointment

urlpatterns = [
    path(r'auth/', include('knox.urls')),
    path(r'profile/', UserProfileDetail.as_view()),
    path(r'user/', UserDetail.as_view()),
    path(r'change-password/', ChangePasswordView.as_view()),
    
    path(r'flats/', FlatsView.as_view()),
    path(r'flats/<int:flat_id>/', FlatView.as_view()),
    path(r'flats/<int:flat_id>/members/', FlatMembersView.as_view()),
    path(r'flats/<int:flat_id>/members/<int:user_id>', FlatMemberView.as_view()),
    path(r'flats/<int:flat_id>/members/<int:user_id>/make_admin', MakeAdminView.as_view()),
    path(r'flats/<int:flat_id>/admins/', FlatAdminsView.as_view()),
    path(r'flats/<int:flat_id>/admins/<int:user_id>', FlatAdminView.as_view()),
    path(r'flats/<int:flat_id>/leave/', LeaveFlat.as_view()),

    path(r'flats/<int:flat_id>/invites/', ListAndCreateInviteView.as_view()),
    path(r'flats/<int:flat_id>/invites/<str:invite_code>', RetrieveDestroyInvite.as_view()),
    path(r'invite/<str:invite_code>/open', OpenInviteView.as_view()),
    path(r'invite/<str:invite_code>/', PublicInviteView.as_view()),

    path(r'flats/<int:flat_id>/chores/', ListCreateFlatChores.as_view()),
    path(r'flats/<int:flat_id>/schedule/', ListChoreAppointments.as_view()),
    path(r'flats/<int:flat_id>/schedule/edit/', ScheduleCreateDeleteView.as_view()),
    path(r'chores/', ListAllUserChores.as_view()),
    path(r'chores/<int:pk>', RetrieveUpdateDestroyChore.as_view()),
    path(r'schedule/<int:pk>', RetrieveUpdateDestroyChoreAppointment.as_view()),
]
