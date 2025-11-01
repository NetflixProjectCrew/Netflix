from django.contrib import admin
from django.utils.html import format_html

from .models import Movie, Genre, Author, Actor, MovieCharacter, Casting
from .tasks import compute_movie_duration, bulk_recompute_durations

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}  # автогенерация slug


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    search_fields = ("name", "bio")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    search_fields = ("name", "bio")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(MovieCharacter)
class MovieCharacterAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class CastingInline(admin.TabularInline):
    model = Casting
    extra = 1
    autocomplete_fields = ("actor", "character")
    fields = ("actor", "character", "credit_order", "is_voice", "is_cameo", "notes")
    ordering = ("credit_order",)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'year', 'author', 'views', 
         'poster_preview',
    )
    list_filter = ('year', 'genres', 'author', 'meta_dirty')
    search_fields = ('title', 'description', 'author__name', 'genres__name')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('genres',)
    autocomplete_fields = ('author',)
    readonly_fields = (
        'views', 'created_at', 'updated_at', 
        'poster_preview',    
    )

    fieldsets = (
        ('Основное', {
            'fields': ('title', 'slug', 'description', 'year', 'author', 'genres')
        }),
        ('Медиа', {
            'fields': (
                'poster', 'video', 'poster_preview'
            ),
        }),
        ('Служебное', {
            'fields': ('views', 'created_at', 'updated_at'),
        }),
    )

    inlines = [CastingInline]
     
    def poster_preview(self, obj):
        if obj.poster:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:4px;" />',
                obj.poster.url
            )
        return "—"
    poster_preview.short_description = "Постер"
 