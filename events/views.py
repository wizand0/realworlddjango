import datetime

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from events.models import Review, Feature, Category, Event


class Eventlist(ListView):
    model = Event
    template_name = 'events/event_list.html'
    paginate_by = 9
    context_object_name = 'events'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['features'] = Feature.objects.all()
        return context


def Eventdetail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    percent = int((event.display_enroll_count() / event.participants_number)
                  * 100) if event.participants_number != 0 else 0
    context = {
        'event': event,
        'percent': percent
    }
    return render(request, 'events/event_detail.html', context)


@require_POST
def create_review(request):

    rate = ''
    text = ''
    created = ''
    user_name = ''
    ok = True
    msg = ''

    event_id = request.POST.get('event_id')
    rate = request.POST.get('rate')
    text = request.POST.get('text')
    user_req = request.user

    if not request.user.is_authenticated:
        user_req = None
        ok = False
    else:
        user_name = user_req.__str__()

    event = Event.objects.get(pk=event_id)
    created = datetime.date.today().strftime('%d.%m.%Y')

    if Review.objects.filter(user=user_req, event=event).exists():
        msg = 'Вы уже отправляли отзыв к этому событию'
        ok = False

    elif not event:
        msg = 'Событие, на которое отправляете комментарий, не найдено!'
        ok = False

    elif text == '' or rate == '':
        msg = 'Оценка и текст отзыва - обязательные поля'
        ok = False

    elif user_req and user_req.is_authenticated:
        # добавляем в БД
        try:
            element = Review(
                user = user_req,
                event = event,
                rate = rate,
                text = text,
                # created = created,
                # updated = created
            )
            element.save()

        except:
            msg = 'комментарий не удалось сохранить в БД! '
            ok = False

    else:
        msg = 'Отзывы могут отправлять только зарегистрированные пользователи'
        ok = False

    form_data = {
        'ok': ok,  # True, если отзыв создан успешно
        'msg': msg,  # Сообщение об ошибке
        'rate': rate,  # оценка, - обязательно
        'text': text,  # текст отзыва - обязательно
        'created': created,  # Дата создания отзыва в формате DD.MM.YYYY
        'user_name': user_name # 'admin'  # user_name, #Полное имя пользователя
    }

    return JsonResponse(form_data)