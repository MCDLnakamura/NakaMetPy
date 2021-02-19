from setuptools import setup

install_requires = [
    'numpy',
    'matplotlib',
]

packages = [
    'nakametpy'
]

console_scripts = [
    # 'sample_lib_cli=sample_lib_cli.call:main',
]


setup(
    name='nakametpy',
    # version='0.1.0', # (2021.01.19)
    version='0.2.0', # (2021.02.18)
    packages=packages,
    install_requires=install_requires,
    url = 'https://github.com/muchojp/NakaMetPy',
    author = 'Yuki Nakamura',
    author_email = 'contact.muchiwo@gmail.com',
    # entry_points={'console_scripts': console_scripts},
)
