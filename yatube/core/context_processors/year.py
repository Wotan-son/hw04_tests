from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    first_now = datetime.today()
    now = int(first_now.strftime('%Y'))
    return {
        'year': now,
    }
