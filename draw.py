import os
from argparse import ArgumentParser

import mapper.tools as tools
import mapper.manage_files as files
from mapper import draw_map


with open(os.path.join(os.getcwd(), 'miscellaneous', 'logo.txt'), 'r') as f:
    logo = f.read()

# Instantiate the parser
parser = ArgumentParser(
    prog='stats_mapper',
    description=f'{logo}\n\nGet geographic maps with countries colored from numeric data, using the 2-digit ISO codes.'
)

# Define the arguments
parser.add_argument(
    'data_file',
    type=str,
    help='Path to the file with the data.'
)
parser.add_argument(
    '-z', '--out_map',
    default=None,
    type=str,
    help='Path to the generated map image.'
)
parser.add_argument(
    '-c', '--separator',
    default=',',
    type=str,
    help='Separator if `file` is a CSV file.'
)
parser.add_argument(
    '-r', '--sheet',
    default='Sheet1',
    type=str,
    help='Sheet where the data are if `file` is a spreadsheet.'
)
parser.add_argument(
    '-u', '--countries_col',
    default='COUNTRY',
    type=str,
    help='Name of the column where the countries are if `file` is a spreadsheet.'
)
parser.add_argument(
    '-n', '--data_col',
    default='DATA',
    type=str,
    help='Name of the column where the numeric data or the labels are if `file` is a spreadsheet.'
)
parser.add_argument(
    '-t', '--task',
    default='values',
    type=str,
    help='How to segment the data to color the countries in bins.'
)
parser.add_argument(
    '-m', '--source_map',
    nargs='*',
    default=None,
    type=lambda x: str(x).lower(),
    help='Map to draw (any combination of "africa", "antarctica", "asia", "europe", "north_america", "oceania", "south'
         '_america" and "world", followed or not followed each one by "*" to include intercontinental territories).'
)
parser.add_argument(
    '-s', '--smart',
    default=True,
    type=tools.str2bool,
    help='Whether to try to fix errors with slight changes in possible wrong parameters.'
)
parser.add_argument(
    '-p', '--palette_style',
    default='RdYlBu',
    type=str,
    help='Palette name or sequence of Hex and/or 3-tuple RGB colors, separated by underscores.'
)
parser.add_argument(
    '-i', '--invert_palette',
    default=False,
    type=tools.str2bool,
    help='Whether to use the palette colors with their order inverted.'
)
parser.add_argument(
    '-f', '--force_default_palette',
    default='Reds',
    type=str,
    help='If "Reds", "Greens" or "Blues" safe default palette to use if the palette assignation fails.'
)
parser.add_argument(
    '-g', '--missing',
    default='#e6e6e6',
    type=str,
    help='Color for the countries that are missing in the data.'
)
parser.add_argument(
    '-o', '--ocean',
    default='255,255,255',
    type=str,
    help='Color for the oceans, seas and lakes in the map.'
)
parser.add_argument(
    '-l', '--add_legend',
    default=1,
    type=int,
    choices=[0, 1, 2],
    help='Whether to show the legend in the map. If 0, do not. If 1, do. If 2, only max and min values are displayed.'
)
parser.add_argument(
    '-k', '--legend_aliases',
    default=None,
    type=str,
    help='Path to a JSON file with the mapping between the labels of each country and their description in the legend.'
)
parser.add_argument(
    '-a', '--language',
    default='math',
    type=str,
    choices=['en', 'es', 'de', 'math', 'nerd'],
    help='Language of the legend. Available ones are "en", "es", "de", "math" and "nerd".'
)
parser.add_argument(
    '-e', '--decimals',
    default=0,
    type=int,
    help='Number of decimals to show in the numbers that appear in the legend.'
)
parser.add_argument(
    '-y', '--colors_used_only',
    default=True,
    type=tools.str2bool,
    help='Whether to delete from the legend the colors and intervals with no countries in them.'
)
parser.add_argument(
    '-b', '--bitmap',
    default=True,
    type=tools.str2bool,
    help='Whether to save the map as a PNG file, or leave it as an SVG file.'
)
parser.add_argument(
    '-d', '--dpi',
    default=96,
    type=int,
    help='DPIs for the image if it is saved in PNG format.'
)
parser.add_argument(
    '-w', '--width',
    default=None,
    type=float,
    help='Width in pixels of the image if it is saved in PNG format. If None, automatic width is set.'
)
parser.add_argument(
    '-x', '--text_box',
    default=None,
    type=str,
    help='Text to add to the image if it is saved in PNG format (useful for custom legends).'
)

# Parse
args = parser.parse_args()

# Get data from the selected file. If the selected file does not have a directory, the default directory is "../"
if not files.file_fields(args.data_file)[0]:
    args.data_file = os.path.join('..', args.data_file)
data = files.load_csv(args.data_file, args.separator) if files.file_fields(args.data_file)[2] in ['.csv', '.txt'] \
    else files.load_sheet(args.data_file, args.sheet, args.countries_col, args.data_col)

# If `out_map` is None, assign the directory of the stats_map project and the file name of `data_file`
if args.out_map is None:
    args.out_map = os.path.join(os.path.join(*os.path.split(os.getcwd())[:-1]),
                                files.file_fields(args.data_file)[1]) + ('.png' if args.bitmap else '.svg')

# Get legend aliases if provided
if args.legend_aliases is not None:
    import json
    with open(args.legend_aliases) as f:
        aliases = json.load(f)
else:
    aliases = None

# Draw map
svg_map = draw_map(
    data=data,
    task=args.task,
    source_map=args.source_map,
    smart=args.smart,
    palette_style=args.palette_style,
    invert_palette=args.invert_palette,
    force_default_palette=args.force_default_palette,
    missing_color=args.missing,
    ocean_color=args.ocean,
    add_legend=args.add_legend,
    aliases=aliases,
    language=args.language,
    decimals=args.decimals,
    colors_used_only=args.colors_used_only,
    text_box=args.text_box
)

# Save map
files.save_map(
    svg_source_code=svg_map,
    path=args.out_map,
    bitmap=args.bitmap,
    dpi=args.dpi,
    width=args.width
)
