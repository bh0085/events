from setuptools import setup

setup(
    name='AERONAUT events',
    version='.1',
    long_description=__doc__,
    include_package_data=True,
    zip_safe=False,
    install_requires=['flask','flask-restful','flask_assets','sqlalchemy','flask-sqlalchemy-session','aniso8601','alembic']
)
