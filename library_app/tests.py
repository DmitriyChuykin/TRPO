from django.test import TestCase
from django.contrib.auth.models import User
from .models import Book, ReaderProfile, BookLoan, Reservation
from django.utils import timezone
from datetime import timedelta


class BookModelTest(TestCase):
    def setUp(self):
        # Подготовка данных для тестов
        self.book = Book.objects.create(
            title="Тестовая книга",
            author="Тестовый автор",
            total_copies=3,
            available_copies=3
        )

    def test_book_creation(self):
        """Тест: книга создается правильно"""
        self.assertEqual(self.book.title, "Тестовая книга")
        self.assertEqual(self.book.author, "Тестовый автор")
        self.assertEqual(self.book.available_copies, 3)
        self.assertEqual(self.book.total_copies, 3)

    def test_book_availability(self):
        """Тест: проверка доступности книги (простая версия)"""
        # Книга доступна если available_copies > 0
        self.assertTrue(self.book.available_copies > 0)

        # Делаем книгу недоступной
        self.book.available_copies = 0
        self.book.save()
        self.assertFalse(self.book.available_copies > 0)


class ReaderProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        # ВРУЧНУЮ создаем профиль
        self.profile = ReaderProfile.objects.create(
            user=self.user,
            role='reader',
            balance=0.00
        )

    def test_profile_creation(self):
        """Тест: профиль создается правильно"""
        self.assertEqual(self.profile.user.username, "testuser")
        self.assertEqual(self.profile.role, "reader")
        self.assertEqual(float(self.profile.balance), 0.00)

    def test_balance_update(self):
        """Тест: баланс можно изменить"""
        self.profile.balance = 100.50
        self.profile.save()

        # Проверяем что баланс сохранился
        updated_profile = ReaderProfile.objects.get(user=self.user)
        self.assertEqual(float(updated_profile.balance), 100.50)


class ReservationTest(TestCase):
    def setUp(self):
        # Создаем пользователя и книгу
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.profile = ReaderProfile.objects.create(user=self.user)

        self.book = Book.objects.create(
            title="Книга для брони",
            author="Автор",
            total_copies=2,
            available_copies=2
        )

    def test_reservation_creation(self):
        """Тест: бронирование создается"""
        # Создаем бронирование
        reservation = Reservation.objects.create(
            user=self.user,
            book=self.book,
            status='pending'
        )

        self.assertEqual(reservation.user.username, "testuser")
        self.assertEqual(reservation.book.title, "Книга для брони")
        self.assertEqual(reservation.status, "pending")


class SimpleBookLoanTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="loan_user",
            password="testpass123"
        )
        self.profile = ReaderProfile.objects.create(user=self.user)

        self.book = Book.objects.create(
            title="Книга для выдачи",
            author="Автор",
            total_copies=1,
            available_copies=1
        )

    def test_loan_creation_simple(self):
        """Тест: простое создание выдачи книги"""
        # Создаем выдачу БЕЗ due_date (используем авто-назначение)
        loan = BookLoan.objects.create(
            user=self.user,
            book=self.book
        )

        self.assertEqual(loan.user.username, "loan_user")
        self.assertEqual(loan.book.title, "Книга для выдачи")
        self.assertEqual(loan.status, "active")


class ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="view_tester",
            password="testpass123"
        )
        self.profile = ReaderProfile.objects.create(user=self.user)

        # Книга для тестов
        self.book = Book.objects.create(
            title="Книга для тестов",
            author="Автор",
            total_copies=1,
            available_copies=1
        )

    def test_home_page(self):
        """Тест: главная страница открывается"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Библиотека будущего")

    def test_book_search_page(self):
        """Тест: страница поиска книг работает"""
        response = self.client.get('/books/')
        self.assertEqual(response.status_code, 200)

    def test_personal_cabinet_requires_login(self):
        """Тест: личный кабинет требует авторизации"""
        response = self.client.get('/cabinet/')
        # Должен перенаправить на страницу входа (код 302)
        self.assertEqual(response.status_code, 302)

    def test_personal_cabinet_with_login(self):
        """Тест: личный кабинет доступен авторизованным"""
        # Логиним пользователя
        login_success = self.client.login(username='view_tester', password='testpass123')
        self.assertTrue(login_success)

        response = self.client.get('/cabinet/')
        self.assertEqual(response.status_code, 200)


class SimpleIntegrationTest(TestCase):
    """Простой интеграционный тест"""

    def test_book_reservation_flow(self):
        """Тест: базовый поток бронирования"""
        # 1. Создаем пользователя и книгу
        user = User.objects.create_user(username="flow_user", password="testpass")
        profile = ReaderProfile.objects.create(user=user)

        book = Book.objects.create(
            title="Тестовая книга для потока",
            author="Автор",
            total_copies=1,
            available_copies=1
        )

        # 2. Проверяем начальное состояние
        self.assertEqual(book.available_copies, 1)
        self.assertEqual(book.total_copies, 1)

        # 3. Создаем бронирование
        reservation = Reservation.objects.create(
            user=user,
            book=book,
            status='pending'
        )

        # 4. Проверяем что бронирование создалось
        self.assertEqual(reservation.user.username, "flow_user")
        self.assertEqual(reservation.book.title, "Тестовая книга для потока")
        self.assertEqual(reservation.status, "pending")


class BasicFunctionalityTest(TestCase):
    """Тесты базового функционала"""

    def test_book_count(self):
        """Тест: можем подсчитать книги"""
        Book.objects.create(title="Книга 1", author="Автор 1", total_copies=1, available_copies=1)
        Book.objects.create(title="Книга 2", author="Автор 2", total_copies=1, available_copies=1)

        book_count = Book.objects.count()
        self.assertEqual(book_count, 2)

    def test_user_authentication(self):
        """Тест: пользователь может аутентифицироваться"""
        user = User.objects.create_user(username="auth_user", password="password123")

        # Проверяем аутентификацию
        auth_success = self.client.login(username='auth_user', password='password123')
        self.assertTrue(auth_success)

    def test_reservation_status(self):
        """Тест: статусы бронирования работают"""
        user = User.objects.create_user(username="status_user", password="testpass")
        profile = ReaderProfile.objects.create(user=user)
        book = Book.objects.create(title="Книга статуса", author="Автор", total_copies=1, available_copies=1)

        reservation = Reservation.objects.create(
            user=user,
            book=book,
            status='pending'
        )

        # Меняем статус
        reservation.status = 'confirmed'
        reservation.save()

        updated_reservation = Reservation.objects.get(id=reservation.id)
        self.assertEqual(updated_reservation.status, 'confirmed')
