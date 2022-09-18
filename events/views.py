
import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseForbidden, HttpResponseRedirect

from .forms import EventEnrollForm, EventFilterForm, EventCreateUpdateForm
from .models import *


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_objects'] = Category.objects.all()
        context['feature_objects'] = Feature.objects.all()
        context['filter_form'] = EventFilterForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('enrolls', 'features', 'reviews').annotate(enroll_count=Count('enrolls'))
        form = EventFilterForm(self.request.GET)
        if form.is_valid():
            category = form.cleaned_data['category']
            features = form.cleaned_data['features']
            date_start = form.cleaned_data['date_start']
            date_end = form.cleaned_data['date_end']
            is_private = form.cleaned_data['is_private']
            is_available = form.cleaned_data['is_available']
            if category:
                queryset = queryset.filter(category=category)
            if features:
                for feature in features:
                    queryset = queryset.filter(features__in=[feature])
            if date_start:
                queryset = queryset.filter(Q(date_start=date_start) | Q(date_start__gt=date_start))
            if date_end:
                queryset = queryset.filter(Q(date_start__lt=date_end) | Q(date_start=date_end))
            if is_private:
                queryset = queryset.filter(is_private=is_private)
            if is_available:
                queryset = queryset.filter(enroll_count__lt=F('participants_number'))
        return queryset.order_by('-pk')

class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        default_object = super().get_object(queryset)
        return default_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = EventEnrollForm(initial={'user': self.request.user, 'event': self.object})
        return context

    def get_template_names(self):
        default_template_names = super().get_template_names()
        return default_template_names


class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    template_name = 'events/event_update.html'
    form_class = EventCreateUpdateForm
    success_url = reverse_lazy('events:event_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['is_auth'] = self.request.user.is_authenticated
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Новое событие успешно создано.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        return super().form_invalid(form)


class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventCreateUpdateForm
    template_name = 'events/event_update.html'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrolls = self.object.enrolls.select_related('user').all()
        reviews = self.object.reviews.select_related('user').all()
        context['reviews'] = reviews
        dict_rev = dict_data(reviews, 'user_id')
        partps = []
        for enr in enrolls:
            user = enr.user
            rate = dict_rev.get(user.id, 0)
            partps.append({'name': user.get_full_name(), 'email': user.email, 'rate': rate})
        context['partps'] = prepare_data(enrolls, dict_rev, 'user', 0, 'user')
        return context

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        return super().form_invalid(form)


class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    template_name = 'events/event_update.html'
    success_url = reverse_lazy('events:event_list')

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        messages.success(request, f'Событие {self.object} удалено.')
        return result

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


class EventEnrollView(LoginRequiredMixin, CreateView):
    model = Enroll
    form_class = EventEnrollForm

    def get_success_url(self):
        return self.object.event.get_absolute_url()

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        event = form.cleaned_data.get('event', None)
        if not event:
            event = get_object_or_404(Event, pk=form.data.get('event'))
        redirect_url = event.get_absolute_url() if event else reverse_lazy('events:event_list')
        return HttpResponseRedirect(redirect_url)

    def form_valid(self, form):
        messages.success(self.request, f'Вы записаны на {form.cleaned_data["event"]} ')
        return super().form_valid(form)