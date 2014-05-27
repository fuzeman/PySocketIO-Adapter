from setuptools import setup

setup(
    name='PySocketIO-Adapter',
    version='0.2.0-beta',
    url='http://github.com/fuzeman/PySocketIO-Adapter/',

    author='Dean Gardiner',
    author_email='me@dgardiner.net',

    packages=['pysocketio_adapter'],
    platforms='any',

    install_requires=[
        'PySocketIO-Parser'
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],
)
