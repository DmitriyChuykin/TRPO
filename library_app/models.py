from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    author = models.CharField(max_length=100, verbose_name="Автор") 
    total_copies = models.IntegerField(default=1, verbose_name="Всего экземпляров")
    available_copies = models.IntegerField(default=1, verbose_name="Доступно экземпляров")
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

class ReaderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Администратор'),
        ('librarian', 'Библиотекарь'), 
        ('reader', 'Читатель'),
    ], default='reader', verbose_name="Роль")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Баланс")
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"
    
    class Meta:
        verbose_name = "Профиль читателя"
        verbose_name_plural = "Профили читателей"

class BookLoan(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    loan_date = models.DateField(verbose_name="Дата выдачи", default=timezone.now)
    due_date = models.DateField(null=True, blank=True, verbose_name="Срок возврата")
    return_date = models.DateField(null=True, blank=True, verbose_name="Дата возврата")
    status = models.CharField(max_length=20, choices=[
        ('active', 'Активна'),
        ('returned', 'Возвращена'),
        ('overdue', 'Просрочена'),
    ], default='active', verbose_name="Статус")
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Штраф")
    
    def calculate_fine(self):
        if self.return_date:
            if self.return_date > self.due_date:
                days_overdue = (self.return_date - self.due_date).days
                return days_overdue * 10
        else:
            if self.due_date and timezone.now().date() > self.due_date:
                days_overdue = (timezone.now().date() - self.due_date).days
                return days_overdue * 10
        return 0
    
    def save(self, *args, **kwargs):
        old_fine = 0
        old_return_date = None
        if self.pk:
            old_loan = BookLoan.objects.get(pk=self.pk)
            old_fine = old_loan.fine
            old_return_date = old_loan.return_date
        
        self.fine = self.calculate_fine()
        
        if self.return_date and not old_return_date:
            try:
                profile = self.user.readerprofile
                profile.balance -= self.fine
                profile.save()
            except ReaderProfile.DoesNotExist:
                pass
        
        if self.return_date:
            self.status = 'returned'
        elif self.due_date and timezone.now().date() > self.due_date:
            self.status = 'overdue'
        else:
            self.status = 'active'
                
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.book.title} - {self.user.username}"
    
    class Meta:
        verbose_name = "Выдача книги"
        verbose_name_plural = "Выдачи книг"

class Reservation(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    reservation_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата бронирования")
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Ожидание'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
    ], default='pending', verbose_name="Статус")
    
    def __str__(self):
        return f"{self.book.title} - {self.user.username}"
    
    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    transaction_type = models.CharField(max_length=20, choices=[
        ('deposit', 'Пополнение'),
        ('fine', 'Штраф'),
        ('payment', 'Оплата'),
    ], verbose_name="Тип операции")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата операции")
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.transaction_type})"
    
    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"