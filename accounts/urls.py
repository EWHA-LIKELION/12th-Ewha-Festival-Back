from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
        path('signup/',SignUpView.as_view()),
        path('login/',LoginView.as_view()),
        path('duplicate/',DuplicateUsernameView.as_view()),
        
]