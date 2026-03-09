from django.contrib import admin
from .models import Book, ReaderProfile, BookLoan, Reservation, Transaction

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'available_copies', 'total_copies']
    search_fields = ['title', 'author']

@admin.register(ReaderProfile)
class ReaderProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'balance']
    list_filter = ['role']
    search_fields = ['user__username']

@admin.register(BookLoan)
class BookLoanAdmin(admin.ModelAdmin):
    list_display = ['book', 'user', 'loan_date', 'due_date', 'return_date', 'status', 'fine']
    list_filter = ['status', 'loan_date']
    search_fields = ['book__title', 'user__username']
    list_editable = ['loan_date', 'due_date', 'return_date', 'status', 'fine']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['book', 'user', 'reservation_date', 'status']
    list_filter = ['status', 'reservation_date']
    search_fields = ['book__title', 'user__username']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'transaction_type', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['user__username']

from django.contrib import admin

admin.site.site_header = 'Панель библиотекаря'
admin.site.site_title = 'Панель библиотекаря'
admin.site.index_title = 'Управление процессами библиотеки'
