from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from blog.models import Post, Category


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
