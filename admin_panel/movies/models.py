import uuid

from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta:
        abstract = True


class FilmWork(UUIDMixin, TimeStampedMixin):
    TYPE_CHOICES = (
        ("movie", _("Movie")),
        ("tv_show", _("TV show")),
    )

    title = models.TextField(
        verbose_name=_("Title"),
    )

    description = models.TextField(
        verbose_name=_("Description"),
        null=True,
        blank=True,
    )

    creation_date = models.DateField(
        verbose_name=_("Creation date"),
        null=True,
        blank=True,
    )

    file_path = models.URLField(
        verbose_name=_("File path"),
        null=True,
        blank=True,
    )

    rating = models.FloatField(
        verbose_name=_("Rating"),
        null=True,
        blank=True,
        validators=(
            MinValueValidator(0),
            MaxValueValidator(100),
        ),
    )

    type = models.TextField(
        verbose_name=_("Type"),
        choices=TYPE_CHOICES,
    )

    genres = models.ManyToManyField(
        "Genre",
        through="GenreFilmWork",
        related_name="film_works",
    )

    persons = models.ManyToManyField(
        "Person",
        through="PersonFilmWork",
        related_name="film_works",
    )

    def __str__(self) -> str:
        return str(self.title)

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = _("Film work")
        verbose_name_plural = _("Film works")
        indexes = [
            models.Index(
                fields=["title"],
                name="film_work_title_idx",
            ),
            models.Index(
                fields=["rating"],
                name="film_work_rating_idx",
            ),
            models.Index(
                fields=["creation_date"],
                name="film_work_creation_date_idx",
            ),
            models.Index(
                fields=["updated_at"],
                name="film_work_updated_at_idx",
            ),
        ]


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.TextField(
        verbose_name=_("Title"),
        unique=True,
    )

    description = models.TextField(
        verbose_name=_("Description"),
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        db_table = 'content"."genre'
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")
        indexes = [
            models.Index(
                fields=["updated_at"],
                name="genre_updated_at_idx",
            ),
        ]


class GenreFilmWork(UUIDMixin):
    genre = models.ForeignKey(
        "Genre",
        on_delete=models.CASCADE,
    )

    film_work = models.ForeignKey(
        "FilmWork",
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self) -> str:
        return f"{self.film_work} - {self.genre}"

    class Meta:
        verbose_name = _("Film genre")
        verbose_name_plural = _("Film genres")
        db_table = 'content"."genre_film_work'
        constraints = [
            models.UniqueConstraint(
                fields=["genre", "film_work"],
                name="genre_film_work_idx",
            ),
        ]
        indexes = [
            models.Index(
                fields=["film_work"],
                name="genre_film_work_id_idx",
            ),
        ]


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.TextField(
        verbose_name=_("Full name"),
    )

    def __str__(self) -> str:
        return str(self.full_name)

    class Meta:
        db_table = 'content"."person'
        verbose_name = _("Person")
        verbose_name_plural = _("People")
        indexes = [
            models.Index(
                fields=["updated_at"],
                name="person_updated_at_idx",
            ),
        ]


class PersonFilmWork(UUIDMixin, TimeStampedMixin):
    ROLE_CHOICES = (
        ("actor", _("Actor")),
        ("director", _("Director")),
        ("writer", _("Writer")),
    )

    person = models.ForeignKey(
        "Person",
        on_delete=models.CASCADE,
    )

    film_work = models.ForeignKey(
        "FilmWork",
        on_delete=models.CASCADE,
    )

    role = models.CharField(
        verbose_name=_("Role"),
        choices=ROLE_CHOICES,
    )

    def __str__(self) -> str:
        return f"{self.film_work} - {self.person} - {self.role}"

    class Meta:
        db_table = 'content"."person_film_work'
        verbose_name = _("People in film")
        verbose_name_plural = _("People in film")
        constraints = [
            models.UniqueConstraint(
                fields=["person", "film_work", "role"],
                name="person_film_work_idx",
            ),
        ]
        indexes = [
            models.Index(
                fields=["film_work"],
                name="person_film_work_id_idx",
            ),
            models.Index(
                fields=["updated_at"],
                name="person_film_work_updated_idx",
            ),
        ]
