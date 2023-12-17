from typing import Any
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse_lazy, reverse

from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin


from .forms import PostForm, ProfileForm, CommentForm
from blog.models import Post, Category, Comment

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
    ).order_by('-pub_date').annotate(comment_count=Count('comments'))


# def index(request):
#     return render(request, 'blog/index.html', {
#         'page_obj': filter_posts(Post.objects)[0:10],
#     })


# def category_posts(request, category_slug):
#     category = get_object_or_404(
#         Category,
#         is_published=True,
#         slug=category_slug,
#     )
#     return render(request, 'blog/category.html',
#                   {'page_obj': filter_posts(category.posts),
#                    'category': category})

class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    ordering = '-created_at'
    paginate_by = 10
    pk_url_kwarg = 'category_slug'

    def get_queryset(self):
        category = get_object_or_404(Category,
                                     is_published=True,
                                     slug=self.kwargs[self.pk_url_kwarg])
        res = filter_posts(category.posts)
        return res


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = '-created_at'
    paginate_by = 10

    def get_queryset(self):
        return filter_posts(Post.objects)


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    queryset = Post.objects.all()
    ordering = ' - pub_date'
    paginate_by = 10

    def get_user(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        if self.request.user != self.get_user():
            return self.get_user().posts.prefetch_related(
                'comments'
            ).select_related(
                'location', 'author', 'category'
            ).annotate(comment_count=Count('comments')).filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            ).order_by('-pub_date')
        return self.get_user().posts.all()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_user()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = ProfileForm

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        obj = queryset.get(username=self.request.user.username)
        return obj

    def get_success_url(self):
        return reverse_lazy('blog:index')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', args=[self.request.user.username]
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    ordering = 'id'
    paginate_by = 10
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != post.author:
            post = get_object_or_404(
                Post,
                pk=self.kwargs[self.pk_url_kwarg],
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )
        return post

    def get_context_data(self, **kwargs):
        return dict(
            super().get_context_data(**kwargs),
            form=CommentForm(),
            comments=self.object.comments.select_related('author'),
        )


class UpdatePostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class DeletePostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile', args=[self.request.user.username]
        )

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class AddCommentCreateView(LoginRequiredMixin, CreateView):
    _post = None
    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self._post = (
            get_object_or_404(
                Post,
                pk=kwargs['post_id'],
            )
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self._post
        return super().form_valid(form)

    def get_success_url(self):
        print(self.kwargs['post_id'])
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm

    def get_object(self):
        comment = get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            author=self.request.user
        )
        return comment

    def get_success_url(self):
        print(self.kwargs['post_id'])
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self):
        comment = get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            author=self.request.user
        )
        instance = get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            author=self.request.user
        )
        if instance.author != self.request.user:
            self.get_success_url(self)
        return comment

    def get_success_url(self):
        print(self.kwargs['post_id'])
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])
