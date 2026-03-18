from django.contrib import admin

from .models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork
    extra = 1


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork
    extra = 1


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmWorkInline, PersonFilmWorkInline)
    list_filter = ("type",)
    list_display = (
        "title",
        "type",
        "creation_date",
        "rating",
    )
    search_fields = (
        "title",
        "description",
        "id",
        "creation_date",
    )
