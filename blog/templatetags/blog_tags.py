from django import template
from ..models import Post
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown

register = template.Library()


@register.simple_tag(name='posts_written')
def posts_written():
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(counter):
    latest_posts = Post.published.order_by('-publish')[:counter]
    return {'latest_posts': latest_posts}


@register.inclusion_tag('blog/comment/most_commented_posts.html')
def most_commented_posts(counter):
    most_commented = Post.published.annotate(most_commented=Count('comments')).order_by('-most_commented')[:counter]
    return {'most_commented_posts': most_commented}


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
