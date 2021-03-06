import os

import uvicorn
from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware
from starlette.templating import Jinja2Templates
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_queryset_creator

from fastapi_admin.depends import get_model
from fastapi_admin.factory import app as admin_app
from fastapi_admin.schemas import BulkIn
from fastapi_admin.site import Site, Menu

TORTOISE_ORM = {
    'connections': {
        'default': os.getenv('DATABASE_URL')
    },
    'apps': {
        'models': {
            'models': ['examples.models'],
            'default_connection': 'default',
        }
    }
}

templates = Jinja2Templates(directory='examples/templates')


@admin_app.post(
    '/rest/{resource}/bulk/test_bulk'
)
async def test_bulk(
        bulk_in: BulkIn,
        model=Depends(get_model)
):
    qs = model.filter(pk__in=bulk_in.pk_list)
    pydantic = pydantic_queryset_creator(model)
    ret = await pydantic.from_queryset(qs)
    return ret.dict()


@admin_app.get(
    '/home',
)
async def home():
    return {
        'html': templates.get_template('home.html').render()
    }


def create_app():
    fast_app = FastAPI(debug=False)
    register_tortoise(fast_app, config=TORTOISE_ORM, generate_schemas=True)
    fast_app.mount('/admin', admin_app)

    fast_app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    return fast_app


app = create_app()


@app.on_event('startup')
async def start_up():
    admin_app.debug = False
    admin_app.init(
        user_model='User',
        tortoise_app='models',
        admin_secret='test',
        permission=True,
        site=Site(
            name='FastAPI-admin Demo',
            logo='https://github.com/long2ice/fastapi-admin/raw/master/front/static/img/logo.png',
            login_footer='FASTAPI ADMIN - FastAPI Admin Dashboard',
            login_description='FastAPI Admin Dashboard',
            locale='en-US',
            locale_switcher=True,
            theme_switcher=True,
            menus=[
                Menu(
                    name='Home',
                    url='/',
                    icon='fa fa-home'
                ),
                Menu(
                    name='Content',
                    title=True
                ),
                Menu(
                    name='Product',
                    url='/rest/Product',
                    icon='icon-list',
                    search_fields=('type',),
                    fields_type={
                        'type': 'radiolist',
                        'image': 'link'
                    },
                    bulk_actions=[
                        {
                            'value': 'delete',
                            'text': 'delete_all',
                        },
                        {
                            'value': 'test_bulk',
                            'text': 'TestBulk'
                        }
                    ],
                    attrs={
                        'name': {'cols': 6},
                        'view_num': {'cols': 3},
                        'sort': {'cols': 3},
                        'created_at': {'cols': 6},
                        'categories': {'cols': 6},
                    }
                ),
                Menu(
                    name='Category',
                    url='/rest/Category',
                    icon='icon-list'
                ),
                Menu(
                    name='Config',
                    url='/rest/Config',
                    icon='fa fa-pencil',
                ),
                Menu(
                    name='External',
                    title=True
                ),
                Menu(
                    name='Github',
                    url='https://github.com/long2ice/fastapi-admin',
                    icon='fa fa-github',
                    external=True
                ),
                Menu(
                    name='Auth',
                    title=True
                ),
                Menu(
                    name='User',
                    url='/rest/User',
                    icon='fa fa-user',
                    exclude=('password',),
                    search_fields=('username',),
                    fields_type={
                        'avatar': 'image'
                    },
                ),
                Menu(
                    name='Role',
                    url='/rest/Role',
                    icon='fa fa-group',
                    actions={
                        'delete': False
                    }
                ),
                Menu(
                    name='Permission',
                    url='/rest/Permission',
                    icon='fa fa-user-plus',
                    actions={
                        'delete': False
                    }
                ),
                Menu(
                    name='Logout',
                    url='/logout',
                    icon='fa fa-lock',
                    actions={
                        'delete': False
                    }
                )
            ]
        )
    )


if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, debug=False, reload=False, lifespan='on')
