from django.contrib import admin
from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'display_event_count', ]
    list_display_links = ['id', 'title', ]


@admin.register(models.Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', ]
    list_display_links = ['id', 'title', ]


class FullnessFilter(admin.SimpleListFilter):
    title = 'Заполненность'
    parameter_name = 'fullness_filter'

    def lookups(self, request, model_admin):
        filter_list = (
            ('1', 'sold-out'),
            ('2', '>50%'),
            ('3', '<= 50%'),
        )
        return filter_list

    def queryset(self, request, queryset):
        events_id = []
        result = ''
        for el in self.lookup_choices:
            if self.value() in el:
                result = el[1]

        for event in queryset:
            sampling_principle = (str(event.display_places_left()).find(result) >= 0)
            if sampling_principle == True:
                events_id.append(event.id)

        return queryset.filter(id__in=events_id)


class ReviewInstanceInline(admin.TabularInline):
    model = models.Review
    extra = 0
    can_delete = False
    readonly_fields = [field.name for field in model._meta.fields]

    def has_add_permission(self, request, obj):
        return False


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'date_start', 'is_private',
                    'participants_number', 'display_enroll_count',
                    'display_places_left', ]
    list_select_related = ['category']
    list_display_links = ['id', 'title', ]
    list_filter = [FullnessFilter, 'category', 'features', ]
    ordering = ['date_start', ]
    filter_horizontal = ['features', ]
    readonly_fields = ['display_enroll_count', 'display_places_left', ]
    search_fields = ['title', ]
    inlines = [ReviewInstanceInline]


@admin.register(models.Enroll)
class EnrollAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'event', 'created', ]
    list_display_links = ['id', 'user', 'event', ]
    list_select_related = ['user', 'event', ]


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'event', 'rate', 'created', 'updated', ]
    list_display_links = ['id', 'user', 'event', ]
    list_filter = ['created', 'event', ]
    list_select_related = ['user', 'event', ]
    fields = ['user', 'event', 'rate', 'text', ('created', 'updated'), 'id']
    readonly_fields = ['created', 'updated', 'id', ]

