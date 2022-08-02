import datetime

from django.shortcuts import render

# Create your views here.
from events.models import Review


@require_POST
def create_review(request):
    event_id = request.POST.get('event_id')
    rate = request.POST.get('rate')
    text = request.POST.get('text')
    ok = True
    created = datetime.date.today().strftime('%d.%m.%Y')
    msg = ''

    event = Event.objects.get(pk=event_id)
    user_request = request.user

    if Review.objects.filter(user=user_request, event=event).exists():
        msg = 'Вы уже оставляли отзыв к этому событию'
        status = False
    elif text == '' or rate == '':
        msg = 'Оценка и текст отзыва - обязательные поля'
        ok = False
    elif not user_request.is_authenticated:
        msg = 'Отзывы могут оставлять только зарегистрированные пользователи'
        ok = False
