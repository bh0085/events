from setuptools import setup

setup(
    name='AERONAUT events',
    version='.1',
    long_description=__doc__,
    include_package_data=True,
    zip_safe=False,
    install_requires=['flask','flask-migrate', 'flask-debugtoolbar','flask-restful','flask_assets','flask-sqlalchemy','sqlalchemy','flask-sqlalchemy-session','aniso8601','alembic', 'pyscss', 'dateparser','gunicorn', 'flask_script']
)
