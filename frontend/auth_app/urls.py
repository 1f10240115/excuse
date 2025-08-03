from django.urls import path
from . import views

app_name = 'auth_app'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('google-signin/', views.google_signin, name='google_signin'),
    path('signout/', views.signout, name='signout'),
    path('user-info/', views.get_user_info, name='user_info'),
    path('auth/', views.auth_page, name='auth_page'),
    path('callback/', views.auth_callback, name='auth_callback'),
] 