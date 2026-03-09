from django.urls import path
from django.contrib.auth import views as auth_views  
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.book_search, name='book_search'),
    path('reserve/<int:book_id>/', views.reserve_book, name='reserve_book'),
    path('cabinet/', views.personal_cabinet, name='personal_cabinet'),
    path('librarian/', views.librarian_dashboard, name='librarian_dashboard'),
    path('confirm/<int:reservation_id>/', views.confirm_reservation, name='confirm_reservation'),
    path('logout/', views.custom_logout, name='logout'),
    path('debug/', views.debug_info, name='debug_info'),
    path('deposit/', views.deposit_balance, name='deposit_balance'),
    path('profile/', views.profile, name='profile'),
    path('top-up-balance/', views.top_up_balance, name='top_up_balance'),
    
   
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]