from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from reviews.models import (Category, Comment, Genre, Review, Title,
                            User)

admin.site.empty_value_display = '-пусто-'
ADDITIONAL_USER_FIELDS = (
    (None, {'fields': ('bio', 'role')}),
)


@admin.register(User)
class UserAdmin(UserAdmin):
    add_fieldsets = UserAdmin.add_fieldsets + ADDITIONAL_USER_FIELDS
    fieldsets = UserAdmin.fieldsets + ADDITIONAL_USER_FIELDS
    list_display = (
        "username", "email", "first_name", "last_name", "role", "is_staff"
    )
    list_filter = ("role", "is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "email", "first_name", "last_name")


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'category', 'year', 'get_genre_list')
    search_fields = ('name', 'category__name', 'genre__name')
    list_filter = ('year', 'category', 'genre')
    list_editable = ('category',)
    list_display_links = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'author', 'text', 'score', 'pub_date')
    search_fields = ('title__name', 'author__username', )
    list_filter = ('pub_date', 'score')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'review', 'author', 'text', 'pub_date')
    search_fields = ('author__username',)
    list_filter = ('pub_date',)
