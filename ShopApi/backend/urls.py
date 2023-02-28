from backend.views import RegisterAccount, LoginAccount, ContactView
from django.urls import path

app_name = 'backend'

urlpatterns = [
    path('user/register', RegisterAccount.as_view(), name='user-register'),
    path('user/login', LoginAccount.as_view(), name='user-login'),
    path('user/contact', ContactView.as_view(), name='user-contact')
]