from setuptools import setup, find_namespace_packages

setup(
    name='semaphore',

    version='0.0.1',

    description='Semaphore',
    long_description="{0}".format(open('README.md').read()),
    long_description_content_type='text/markdown',

    url='https://github.com/dgoldsb/semaphore',

    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    package_data={},
    namespace_packages=[],

    setup_requires=[],

    install_requires=[],

    tests_require=[
    ],

    classifiers=[
        'Private :: Do NOT upload to PyPi server',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)