from distutils.core import setup

setup(
    name='stats_mapper',
    version='1.0',
    description='Get geographic maps with countries colored from data, using the 2-digit ISO codes.',
    author='Gonzalo Fuertes Sémelas',
    author_email='gfsemelas@gmail.com',
    url='https://github.com/gfsemelas/stats_mapper/',
    packages=['cairosvg', 'easygui', 'numpy', 'pandas']
)
