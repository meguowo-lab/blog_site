from sqladmin import Admin

from .views import AccountView, BlogPostsView, PermissionsView


def add_admin(admin: Admin):
    admin.add_model_view(AccountView)
    admin.add_model_view(BlogPostsView)
    admin.add_model_view(PermissionsView)
