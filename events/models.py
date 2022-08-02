from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from realworlddjango import settings


class Category(models.Model):
    title = models.CharField(max_length=90, default='', verbose_name='Категория')

    def display_event_count(self):
        # Можно получить количество всех элементов в квэрисэте - метод count():
        # def book_count(self):
        # return self.books.count()
        return self.events.count()

    # display_options.short_description = 'Options'
    # Из лекции Настройка страницы списка
    display_event_count.short_description = 'Всего событий'

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Feature(models.Model):
    title = models.CharField(max_length=90, default='', verbose_name='Свойство события')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Свойство события'
        verbose_name_plural = 'Свойства события'


class Event(models.Model):
    title = models.CharField(max_length=200, default='', verbose_name='Название события')
    description = models.TextField(default='', verbose_name='Описание события')
    date_start = models.DateTimeField(verbose_name='Дата начала события')
    participants_number = models.PositiveSmallIntegerField(default=0, verbose_name='Количество билетов')
    is_private = models.BooleanField(default=False, verbose_name='Частное?')
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.CASCADE, related_name='events')
    features = models.ManyToManyField(Feature, blank=True)
    logo = models.ImageField(upload_to='events/all_events', blank=True, null=True, verbose_name="Загрузить изображение")

    def get_absolute_url(self):
        return reverse('events:event_detail', args=[str(self.pk)])

    def logo_url(self):
        return self.logo.url if self.logo else f'{settings.STATIC_URL}images/svg-icon/event.svg'

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'

    def __str__(self):
        return self.title

    def display_enroll_count(self):
        return self.enrolls.count()

    # display_options.short_description = 'Options'
    # Из лекции Настройка страницы списка
    display_enroll_count.short_description = 'Количество записей'

    def display_places_left(self):
        available = (self.participants_number - self.enrolls.count())
        value = ''
        if available == 0:
            value = f'{available} (sold-out)'
        elif available <= (self.participants_number / 2) and available != 0:
            value = f'{available} (>50%)'
        elif available > (self.participants_number / 2):
            value = f'{available} (<= 50%)'
        return value

    # display_options.short_description = 'Options'
    # Из лекции Настройка страницы списка
    display_places_left.short_description = 'Сколько мест осталось?'


class Enroll(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='enrolls')
    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE, related_name='enrolls')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.event.title} - {self.user}'

    class Meta:
        verbose_name = 'Запись на событие'
        verbose_name_plural = 'Записи на событие'


class Review(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='reviews')
    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE, related_name='reviews')
    rate = models.PositiveSmallIntegerField(default=0)
    text = models.TextField(max_length=500, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.rate} - {self.event.title}'

    class Meta:
        verbose_name = 'Отзыв на событие'
        verbose_name_plural = 'Отзывы на события'
