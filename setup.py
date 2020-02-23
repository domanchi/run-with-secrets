from setuptools import find_packages
from setuptools import setup


setup(
    name='run-with-secrets',
    packages=find_packages(exclude=['test*', 'tmp*']),
    author='Aaron Loo',
    author_email='admin@aaronloo.com',
    entry_points={
        'console_scripts': [
            'run-with-secrets = run_with_secrets.__main__:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'Environment :: Console',
        'Operating System :: OS Independent',
    ],
)