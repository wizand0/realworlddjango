
import datetime

from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from .models import *


def event_list(request):
    template_name = 'events/event_list.html'
    event_objects = Event.objects.all()
    context = {'event_objects': event_objects}
    return render(request, template_name, context)

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    context = {'event': event}
    return render(request, 'events/event_detail.html', context)


@require_POST
def create_review(request):
    data = {
        'ok': True,
        'msg': '',
        'rate': request.POST.get('rate'),
        'text': request.POST.get('text'),
        'created': datetime.date.today().strftime('%d.%m.%Y'),
        'user_name': ''
    }

    pk = request.POST.get('event_id', '')
    if not pk:
        data['msg'] = 'Событие не найдено'
        data['ok'] = False
        return JsonResponse(data)

    else:
        event = Event.objects.get(pk=pk)

        if not request.user.is_authenticated:
            data['msg'] = 'Отзывы могут отправлять только зарегистрированные пользователи'
            data['ok'] = False
            return JsonResponse(data)

        data['user_name'] = request.user.__str__()

        if Review.objects.filter(user=request.user, event=event).exists():
            data['msg'] = 'Вы уже отправляли отзыв к этому событию'
            data['ok'] = False

        elif data['text'] == '' or data['rate'] == '':
            data['msg'] = 'Оценка и текст отзыва - обязательные поля'
            data['ok'] = False

        else:
            new_review = Review(
                user=request.user,
                event=event,
                rate=data['rate'],
                text=data['text'],
                created=data['created'],
                updated=data['created']
            )

            new_review.save()

        return JsonResponse(data)