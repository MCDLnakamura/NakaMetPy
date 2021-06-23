from setuptools import setup, find_packages

# install_requires = [
#     'numpy>=1.17.0',
#     'matplotlib>=3.0.0',
#     'nose>=1.2.0',]

def _requires_from_file(filename):
    return open(filename).read().splitlines()


# packages = ['src', 'tests']


console_scripts = [
    # 'sample_lib_cli=sample_lib_cli.call:main',
]


setup(
    name='nakametpy',
    python_requires='>=3.6.0',
    # version='0.1.0', # (2021.01.19)
    # version='0.2.8', # (2021.02.20)
    # version='1.0.0', # (2021.06.04)
    version='2021.6.2', # (2021.06.04)
    description='Meteorological modules for calculation and colormap.',
    # packages=packages,
    packages=find_packages('src'),
    # install_requires=install_requires,
    install_requires=_requires_from_file('requirements.txt'),
    url = 'https://github.com/muchojp/NakaMetPy',
    author = 'muchojp',
    author_email = 'contact.muchiwo@gmail.com',
    license='BSD 3-clause',
    # entry_points={'console_scripts': console_scripts},
    # long_description=open('README.md', encoding='UTF-8').read(),
    long_description=open('README.md', encoding='UTF-8').read(),
    long_description_content_type="text/markdown",
)
