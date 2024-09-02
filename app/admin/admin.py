from sqladmin import Admin

from .views import AccountView, BlogPostView, PermissionsView, CommentView


def add_admin(admin: Admin):
    admin.add_model_view(AccountView)
    admin.add_model_view(BlogPostView)
    admin.add_model_view(PermissionsView)
    admin.add_model_view(CommentView)
