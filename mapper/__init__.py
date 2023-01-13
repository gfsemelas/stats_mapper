__docformat__ = 'restructuredtext'

# Let users know if they're missing any of our hard dependencies
hard_dependencies = ('pandas', 'numpy', 'cairosvg')
missing_dependencies = []

for dependency in hard_dependencies:
    try:
        __import__(dependency)
    except ImportError as e:
        missing_dependencies.append(f'{dependency}: {e}')

if missing_dependencies:
    raise ImportError(
        'Unable to import required dependencies:\n' + '\n'.join(missing_dependencies)
    )
del hard_dependencies, dependency, missing_dependencies


from mapper import tools
from mapper import manage_files
from mapper import transform
from mapper.drawer import draw_map
