from setuptools import setup, find_packages

setup(
    name='dash_theme_picker',
    version='0.0.1',
    author='rishiNigam',
    author_email='rishinigam1304@gmail.com',
    description='A dash plugin that adds a theme picker (light/dark/custom) to Dash apps',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'dash>=3.0.3'
    ],
    classifiers=[
        'Framework :: Dash',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)