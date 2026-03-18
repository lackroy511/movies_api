from django.db.models import Prefetch
from typing import Any, cast
from django.db.models.query import QuerySet
from django.http import JsonResponse, Http404
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from movies.models import FilmWork, PersonFilmWork


class MoviesApiMixin:
    model = FilmWork
    http_method_names: list[str] = ["get"]

    def get_queryset(self) -> QuerySet[FilmWork]:
        return self.model.objects.prefetch_related(
            "genres",
            Prefetch(
                "personfilmwork_set",
                queryset=PersonFilmWork.objects.select_related("person"),
            ),
        ).all()

    def build_movie_item(self, movie: FilmWork) -> dict[str, Any]:
        return {
            "id": movie.id,
            "title": movie.title,
            "description": movie.description,
            "creation_date": movie.creation_date,
            "rating": movie.rating if movie.rating else 0.0,
            "type": movie.type,
            "genres": [genre.name for genre in movie.genres.all()],
            "actors": [
                person_rel.person.full_name
                for person_rel in movie.personfilmwork_set.all()  # ty: ignore
                if person_rel.role == "actor"
            ],
            "directors": [
                person_rel.person.full_name
                for person_rel in movie.personfilmwork_set.all()  # ty: ignore
                if person_rel.role == "director"
            ],
            "writers": [
                person_rel.person.full_name
                for person_rel in movie.personfilmwork_set.all()  # ty: ignore
                if person_rel.role == "actor"
            ],
        }

    def render_to_response(
        self,
        context: dict[str, list],
        **response_kwargs: dict[str, Any],
    ) -> JsonResponse:
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(
        self,
        *,
        object_list: None = None,
        **kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        movies = self.get_queryset()
        paginator, page, _, _ = self.paginate_queryset(movies, self.paginate_by)
        results = []
        data = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.previous_page_number() if page.has_previous() else None,  # ty: ignore
            "next": page.next_page_number() if page.has_next() else None,  # ty: ignore
            "results": results,
        }
        for movie in movies:
            item = self.build_movie_item(movie)
            results.append(item)

        return data


class MovieDetailApi(MoviesApiMixin, BaseDetailView):
    model = FilmWork
    http_method_names: list[str] = ["get"]

    def get_context_data(
        self,
        *,
        object_list: None = None,
        **kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        obj = self.get_object()
        if not obj:
            raise Http404("Movie not found")

        return self.build_movie_item(cast(FilmWork, obj))
