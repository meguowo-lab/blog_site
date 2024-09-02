from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware

from app import add_admin, auth_backend, auth_router, database
from app.controllers.managers.model import ModelManager
from app.database.db import SessionDep
from app.models.account import BlogPost

app = FastAPI()

static_files = StaticFiles(directory="static")
app.mount("/static", static_files)

app.add_middleware(SessionMiddleware, **auth_backend.middlewares[0].kwargs)  # type: ignore

app.include_router(auth_router)

admin = Admin(
    app,
    session_maker=database.sessionmaker,
    authentication_backend=auth_backend,
    templates_dir="static",
)
templates = admin.templates

add_admin(admin)


@app.get("/", name="blog")
async def blog_view(req: Request, session: SessionDep):
    posts = await ModelManager(model=BlogPost, session=session).get_many()
    return await templates.TemplateResponse(
        req, "templates/blog_all.jinja2", {"posts": posts}
    )


@app.get("/{post_id}", name="post")
async def post_view(req: Request, post_id: int, session: SessionDep):
    post = await ModelManager(model=BlogPost, session=session).get_one(id=post_id)
    return await templates.TemplateResponse(
        req, "templates/blog_one.jinja2", {"post": post}
    )
