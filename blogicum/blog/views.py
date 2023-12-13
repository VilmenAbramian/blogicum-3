from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from blog.models import Post, Category
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.contrib.auth import get_user_model

User = get_user_model()


def filter_posts(posts):
    return posts.select_related(
        'location',
        'category',
        'author',
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )


def index(request):
    return render(request, 'blog/index.html', {
        'post_list': filter_posts(Post.objects)[0:5],
    })


def post_detail(request, post_id):
    return render(request,
                  'blog/detail.html',
                  {'post': get_object_or_404(filter_posts(Post.objects),
                                             pk=post_id)})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        is_published=True,
        slug=category_slug,
    )
    return render(request, 'blog/category.html',
                  {'post_list': filter_posts(category.posts),
                   'category': category})

def todo_create(request):
    pass

def edit_profile():
    pass

class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    queryset = Post.objects.all()
    ordering = 'id'
    paginate_by = 10

    def get_user(self):
        return get_object_or_404(User, username=self.kwargs['username'])
    
    def get_queryset(self) -> QuerySet[Any]:
        if self.request.user != self.get_user():
            return self.get_user().posts.prefetch_related(
                'comments'
            ).select_related(
                'location', 'author', 'category'
            ).filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )
        return self.get_user().posts.all()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_user()
        return context