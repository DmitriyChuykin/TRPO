from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.contrib import messages
from decimal import Decimal
from .models import Book, Reservation, BookLoan, ReaderProfile, Transaction

# STYLES
DARK_THEME_STYLE = """
<style>
    body { 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
        background: #121212; 
        color: #e0e0e0; 
        margin: 0; 
        padding: 0; 
        min-height: 100vh;
        display: flex;
        flex-direction: column;
    }
    .dashboard-wrapper { display: flex; justify-content: center; align-items: center; flex-grow: 1; padding: 40px; }
    .container { max-width: 600px; width: 100%; background: #1e1e1e; padding: 40px; border-radius: 8px; border: 1px solid #333; box-shadow: 0 4px 15px rgba(0,0,0,0.5); text-align: center; }

    /* Landing Styles */
    .landing-hero { text-align: center; padding: 80px 20px 40px; max-width: 800px; margin: 0 auto; }
    .landing-title { font-size: 3em; font-weight: 700; color: #fff; margin-bottom: 10px; letter-spacing: -1px; }
    .landing-subtitle { font-size: 1.2em; color: #aaa; font-weight: 300; margin-bottom: 50px; }
    .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px; max-width: 1000px; margin: 0 auto 60px; padding: 0 20px; }
    .feature-card { background: #1e1e1e; padding: 30px; border-radius: 8px; border: 1px solid #333; transition: transform 0.2s, border-color 0.2s; }
    .feature-card:hover { transform: translateY(-5px); border-color: #3f51b5; }
    .feature-title { color: #fff; font-size: 1.2em; margin-bottom: 10px; font-weight: 600; }
    .feature-text { color: #888; font-size: 0.95em; line-height: 1.5; }
    .cta-section { background: #1a1a1a; padding: 60px 20px; text-align: center; border-top: 1px solid #333; margin-top: auto; }

    /* Elements */
    h1 { color: #fff; font-weight: 400; margin-bottom: 20px; border-bottom: 1px solid #333; padding-bottom: 15px; }
    p { color: #aaa; line-height: 1.6; }
    .btn { display: inline-block; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 14px; text-transform: uppercase; transition: background 0.3s; margin: 10px; cursor: pointer;}
    .btn-primary { background: #3f51b5; color: white; border: none;}
    .btn-primary:hover { background: #303f9f; }
    .btn-large { padding: 16px 40px; font-size: 16px; letter-spacing: 1px; }
    .btn-secondary { background: #424242; color: white; border: 1px solid #555; }
    .btn-secondary:hover { background: #616161; }
    .btn-danger { color: #cf6679; border: 1px solid #cf6679; padding: 10px 20px; }
    .btn-danger:hover { background: rgba(207, 102, 121, 0.1); }
    .badge { background: #2c2c2c; padding: 5px 10px; border-radius: 4px; color: #fff; font-family: monospace; }
</style>
"""


def home(request):
    if request.user.is_authenticated:
        try:
            profile = request.user.readerprofile
            user_role = profile.role
        except:
            if request.user.is_staff or request.user.is_superuser:
                user_role = 'django_admin'
            else:
                user_role = 'reader'

        content = f"{DARK_THEME_STYLE}<div class='dashboard-wrapper'><div class='container'>"

        if user_role == 'django_admin':
            content += f"""
                <h1>Панель Администратора</h1>
                <p>Пользователь: <span class='badge'>{request.user.username}</span></p>
                <div style="margin: 30px 0;">
                    <a href="/admin/" class="btn btn-primary">База данных</a>
                    <a href="/librarian/" class="btn btn-secondary">Интерфейс библиотекаря</a>
                </div>
            """
        elif user_role in ['librarian', 'admin']:
            content += f"""
                    <h1>Панель библиотекаря</h1>
                    <p>Сотрудник: <span class='badge'>{request.user.username}</span></p>
                    <div style="margin: 30px 0;">
                        <a href="/librarian/" class="btn btn-primary">Перейти в панель</a>
                        <a href="/books/" class="btn btn-secondary">Каталог книг</a>
                        <a href="/cabinet/" class="btn btn-secondary">Личный кабинет</a>
                    </div>
                """
        else:  # reader
            content += f"""
                <h1>Личный кабинет</h1>
                <p>Добро пожаловать, <span class='badge'>{request.user.username}</span></p>
                <div style="margin: 30px 0;">
                    <a href="/cabinet/" class="btn btn-primary">Мой кабинет</a>
                    <a href="/books/" class="btn btn-secondary">Поиск книг</a>
                </div>
            """

        content += """<div style="margin-top: 30px; border-top: 1px solid #333; padding-top: 20px;">
                        <a href="/logout/" class="btn-danger">Выход из системы</a>
                      </div></div></div>"""
        return HttpResponse(content)

    else:
        return HttpResponse(f"""
        {DARK_THEME_STYLE}
        <div class="landing-hero">
            <div class="landing-title">Библиотека будущего</div>
            <div class="landing-subtitle">Современный сервис для поиска, бронирования и управления знаниями.</div>
        </div>
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-title">Быстрый поиск</div>
                <div class="feature-text">Мгновенный доступ к электронному каталогу тысяч изданий с удобной фильтрацией по авторам и названиям.</div>
            </div>
            <div class="feature-card">
                <div class="feature-title">Онлайн бронирование</div>
                <div class="feature-text">Забудьте об очередях. Забронируйте нужную книгу в один клик и заберите её в удобное время.</div>
            </div>
            <div class="feature-card">
                <div class="feature-title">Личный контроль</div>
                <div class="feature-text">Удобный кабинет читателя для отслеживания сроков возврата, истории чтений и текущего баланса.</div>
            </div>
        </div>
        <div class="cta-section">
            <p style="color: #fff; font-size: 1.1em; margin-bottom: 20px;">Чтобы воспользоваться сервисом, войдите в аккаунт</p>
            <a href="/accounts/login/" class="btn btn-primary btn-large">Войти в систему</a>
        </div>
        """)


def book_search(request):
    books = Book.objects.all()
    query = request.GET.get('q', '')
    if query:
        books = books.filter(title__icontains=query) | books.filter(author__icontains=query)
    return render(request, 'book_search.html', {'books': books, 'query': query})


@login_required
def reserve_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if book.available_copies > 0:
        reservation = Reservation.objects.create(user=request.user, book=book, status='pending')
        book.available_copies -= 1
        book.save()
        return HttpResponse(f"""
        {DARK_THEME_STYLE}
        <div class="dashboard-wrapper"><div class="container">
            <h1 style="color: #81c784; border-color: #81c784;">Бронирование успешно</h1>
            <p>Вы забронировали книгу: <br><strong style="color: white; font-size: 1.2em;">{book.title}</strong></p>
            <p>Текущий статус: <span style="color: #ffb74d;">Ожидание подтверждения</span></p>
            <div style="margin-top: 30px;">
                <a href="/books/" class="btn btn-primary">Вернуться к поиску</a>
                <a href="/cabinet/" class="btn btn-secondary">Мой кабинет</a>
            </div>
        </div></div>
        """)
    else:
        return HttpResponse(f"""
        {DARK_THEME_STYLE}
        <div class="dashboard-wrapper"><div class="container">
            <h1 style="color: #cf6679; border-color: #cf6679;">Ошибка бронирования</h1>
            <p>Книга <strong>"{book.title}"</strong> временно отсутствует.</p>
            <div style="margin-top: 30px;"><a href="/books/" class="btn btn-primary">Вернуться к поиску</a></div>
        </div></div>
        """)


@login_required
def personal_cabinet(request):
    reservations = Reservation.objects.filter(user=request.user, status='pending')
    active_loans = BookLoan.objects.filter(user=request.user, status='active')
    returned_loans = BookLoan.objects.filter(user=request.user, status='returned')
    try:
        profile = request.user.readerprofile
    except:
        profile = None
    return render(request, 'personal_cabinet.html', {
        'reservations': reservations, 'active_loans': active_loans,
        'returned_loans': returned_loans, 'profile': profile,
    })


def is_librarian(user):
    try:
        return user.readerprofile.role in ['librarian', 'admin']
    except:
        return False


@login_required
@user_passes_test(is_librarian)
def librarian_dashboard(request):
    from django.utils import timezone
    pending_reservations = Reservation.objects.filter(status='pending')
    active_loans = BookLoan.objects.filter(status='active')
    overdue_loans = BookLoan.objects.filter(status='active', due_date__lt=timezone.now())
    return render(request, 'librarian_dashboard.html', {
        'pending_reservations': pending_reservations, 'active_loans': active_loans, 'overdue_loans': overdue_loans,
    })


@login_required
@user_passes_test(is_librarian)
def confirm_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if reservation.status == 'pending':
        reservation.status = 'confirmed'
        reservation.save()
        from django.utils import timezone
        from datetime import timedelta
        loan = BookLoan.objects.create(user=reservation.user, book=reservation.book,
                                       due_date=timezone.now() + timedelta(days=14))
        return HttpResponse(f"""
        {DARK_THEME_STYLE}
        <div class="dashboard-wrapper"><div class="container">
            <h1 style="color: #81c784;">Выдача подтверждена</h1>
            <div style="background: #2c2c2c; padding: 20px; border-radius: 4px; text-align: left; margin: 20px 0;">
                <p>Книга: <strong style="color: white;">{reservation.book.title}</strong></p>
                <p>Читатель: <strong style="color: white;">{reservation.user.username}</strong></p>
                <p>Срок возврата: <strong style="color: #ffb74d;">{loan.due_date.strftime('%d.%m.%Y')}</strong></p>
            </div>
            <a href="/librarian/" class="btn btn-primary">Вернуться в панель</a>
        </div></div>
        """)
    return redirect('librarian_dashboard')


def custom_logout(request):
    logout(request)
    return HttpResponse(f"""
    {DARK_THEME_STYLE}
    <div class="dashboard-wrapper"><div class="container">
        <h1>Сеанс завершен</h1>
        <p>Вы успешно вышли из системы.</p>
        <a href="/" class="btn btn-primary">На главную страницу</a>
    </div></div>
    """)


@login_required
def debug_info(request):
    return redirect('home')  # Заглушка


@login_required
def deposit_balance(request):
    return render(request, 'deposit_balance.html')  # Не используется, есть top-up


@login_required
def profile(request):
    return personal_cabinet(request)  # Перенаправляем на кабинет


@login_required
def top_up_balance(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount = Decimal(amount)
            if amount <= 0:
                messages.error(request, 'Сумма должна быть больше нуля')
                return redirect('top_up_balance')
            profile, created = ReaderProfile.objects.get_or_create(user=request.user)
            profile.balance += amount
            profile.save()
            Transaction.objects.create(user=request.user, amount=amount, transaction_type='deposit',
                                       description=f'Пополнение баланса на {amount} руб.')
            messages.success(request, f'Баланс успешно пополнен на {amount} руб.')
            return redirect('personal_cabinet')
        except:
            messages.error(request, 'Введите корректную сумму')
            return redirect('top_up_balance')
    try:
        profile = ReaderProfile.objects.get(user=request.user)
        balance = profile.balance
    except:
        balance = 0
    return render(request, 'top_up_balance.html', {'balance': balance})
