from setuptools import setup, find_packages

setup(
    name='django-scratchy',
    author='Jaco du Plessis',
    author_email='jaco@jacoduplessis.co.za',
    description='Manage and run Scrapy spiders in Django',
    url='https://github.com/jacoduplessis/scratchy',
    keywords='django scrapy celery',
    version='0.2.2',
    packages=find_packages(),
    install_requires=[
        'django',
        'celery',
        'scrapy',
        'pandas',
        'openpyxl',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
