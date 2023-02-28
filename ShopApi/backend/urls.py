from backend.views import RegisterAccount, LoginAccount
from django.urls import path

app_name = 'backend'

urlpatterns = [
    path('user/register', RegisterAccount.as_view(), name='user-register'),
    path('user/login', LoginAccount.as_view(), name='user-login')
]