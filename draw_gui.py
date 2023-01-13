import os
import easygui

import mapper.tools as tools
import mapper.manage_files as files
from mapper import draw_map


with open(os.path.join(os.getcwd(), 'miscellaneous', 'logo.txt'), 'r') as f:
    logo = f.read()

# Main window of the GUI
start = easygui.ccbox(
    msg=f'{logo}\n\n\nWelcome to stats_mapper, where you can get your geographic maps with countries colored from quant'
        f'itative or qualitative data, using the 2-digit ISO codes.\n\nThis is the guided graphic user interface of sta'
        f'ts_mapper. To start off building your map, choose a file with the data (a spreadsheet or a CSV with the 2-dig'
        f'it ISO codes in a column and the data in another).',
    title='stats_mapper',
    choices=['Choose data file', 'Exit'],
    default_choice='Choose data file',
    cancel_choice='Exit'
)
if not start:
    raise SystemExit


# Select data file window
data_file = easygui.fileopenbox(
    msg='Data file selection',
    title='stats_mapper',
    default=os.getcwd(),
    filetypes=[['*.csv', '*.txt', 'CSV files'], ['*.xlsx', '*.xls', '*.ods', 'Spreadsheets']]
)
if data_file is None:
    raise SystemExit


# Configuration for the selected file
if files.file_fields(data_file)[2] in ['.csv', '.txt']:
    sep = easygui.multenterbox(
        msg='You have selected a CSV file. In order stats_mapper to work properly, this file should have two columns wi'
            'th no header. The first column must contain the 2-digit ISO codes of the countries you wish to color, and '
            'the second column must contain the numeric values. Please, select the CSV separator here.',
        title='stats_mapper - CSV configuration',
        fields=['CSV separator:'],
        values=[',']
    )
    if sep is None:
        raise SystemExit
    data = files.load_csv(data_file, sep)
else:
    spreadsheet_conf = easygui.multenterbox(
        msg='You have selected a spreadsheet file. In order stats_mapper to work properly, this file should have a head'
            'er in the first row. Please, provide the name of the sheet where your data are and the name of the columns'
            ' with the countries and the numeric data or the labels.\n\nNOTE: Python cannot read a spreadsheet file if '
            'it is open, so make sure to close it if necessary.',
        title='stats_mapper - Spreadsheet configuration',
        fields=['Sheet name:', 'Countries 2-digit ISO codes column:', 'Data column:'],
        values=['Sheet1', 'COUNTRY', 'DATA']
    )
    if spreadsheet_conf is None:
        raise SystemExit
    sheet, country_col, data_col = spreadsheet_conf
    data = files.load_sheet(data_file, sheet, country_col, data_col)


# Configuration of the map
map_conf = easygui.multenterbox(
    msg='Select the features for the map.\n\n- Task: how to segment the data to color the countries in bins. Options ar'
        'e:\n    + "values": a color per numeric value.\n    + "b:{n}", where {n} is a positive integer: divide all num'
        'eric data in this number of equally distributed bins and associate a color to each bin.\n    + "t:{s}", where '
        '{s} is a comma-separated string of numbers: numeric thresholds in which to divide the bins.\n    + "sign", "me'
        'an" / "average", "median" or "std": two bins containing all data over and under the selected metric.\n[Example'
        's: "b:4", "t:4,8,20", "t:1m,1,1K,1M", "average"]\n\n- Source map: comma-separated string of continents that sh'
        'ould appear in the map. To ensure that a continent includes countries with part of their territory in other co'
        'ntinents, add an asterisk "*" at the end of its name. Possible continents are: "Africa", "Antarctica", "Asia",'
        ' "Europe", "North America", "Oceania" and "South America". For the whole world to appear, indicate "World". (N'
        'ames are not case-sensitive).\n[Examples: "Europe*", "africa", "North America, South America"]\n\n- Smart: if '
        '"Yes", the program will try to fix all possible errors that arise due to wrong inputs with default values. If '
        '"No", the program will rise the first error it encounters.\n\n- Add legend: 0 to hide it, 1 to show it, 2 to s'
        'how only maximum and minimum values.',
    title='stats_mapper - Map configuration',
    fields=['Task:', 'Source map:', 'Smart:', 'Add legend:'],
    values=['values', 'World', 'Yes', '1']
)
if map_conf is None:
    raise SystemExit
task, source_map, smart, add_legend = map_conf
source_map = [m.lower().strip().replace(' ', '_') for m in source_map.split(',')]
smart = tools.str2bool(smart)
add_legend = 1 if tools.str2num(add_legend) not in range(3) and smart else tools.str2num(add_legend)


# Configuration of the colors
color_conf = easygui.multenterbox(
    msg='Select the color configuration for the map.\n\n- Palette style: palette name (as of https://colorbrewer2.org/)'
        ' or sequence of Hex and/or 3-tuple RGB colors, separated by underscores. If the sequence of colors is chosen, '
        'it should include as many colors as bins in which the data have been segmented with parameter `Task`.\n[Exampl'
        'es: "PuBuGn", "Spectral", "200,50,50_150,100,100", "#fc8d59_98,34,143_#ef8a62"]\n\n- Invert palette: palettes '
        'are an ordered sequence of colors. It could be possible that the red is associated with the lowest datum and t'
        'he blue with the highest in the map, and you want that upside down. This parameter allows you to do this by se'
        'tting it to "Yes" or "No".\n\n- Force default palette: if the `Palette style` input contains errors or the req'
        'uested palette does not have enough colors, `Smart` parameter will try to fix this. If `Smart` is not activate'
        'd, or it is but cannot fix the problem, this parameter allows you to use a safe palette without crashing the p'
        'rogram if its value is "Reds", "Greens" or "Blues", using then the corresponding palette.\n\n- Missing: Hex or'
        ' 3-tuple RGB color which should fill the countries in the map that do not appear in the data.\n\n- Ocean: Hex '
        'or 3-tuple RGB color which should fill the ocean, seas and lakes in the map.',
    title='stats_mapper - Color configuration',
    fields=['Palette style:', 'Invert palette:', 'Force default palette:', 'Missing:', 'Ocean:'],
    values=['RdYlBu', 'No', 'Reds', '#e6e6e6', '255,255,255']
)
if color_conf is None:
    raise SystemExit
palette_style, invert_palette, force_default_palette, missing, ocean = color_conf
invert_palette = tools.str2bool(invert_palette)


if add_legend:
    # Configuration of the legend: aliases or language
    legend_desc_conf = easygui.multenterbox(
        msg='Select configuration for the legend.\n\n- Legend aliases: if your data is qualitative and not quantitative'
            ', you will have used integer labels for countries in the data file and given "values" in parameter `Task`.'
            ' If you wish to use your qualitative identifiers and not the numeric labels, indicate "Yes" here and a fil'
            'e-selection window will appear, where you should select a JSON file that acts as a Python dictionary mappi'
            'ng the labels (keys) with the qualitative identifiers (values).\n\n- Language: if `Legend aliases` is "No"'
            ', the legend will show numeric intervals in the provided language. Choose here that language among "en" (E'
            'nglish), "es" (Spanish), "de" (German), "math" (mathematical style) and "nerd" (algebraic style).',
        title='stats_mapper - Legend aliases or language configuration',
        fields=['Legend aliases:', 'Language:'],
        values=['No', 'math']
    )
    if legend_desc_conf is None:
        raise SystemExit
    legend_aliases, language = legend_desc_conf
    if tools.str2bool(legend_aliases):
        aliases_file = easygui.fileopenbox(
            msg='Legend aliases file selection',
            title='stats_mapper',
            default=os.getcwd(),
            filetypes=['*.json', 'JSON']
        )
        if aliases_file is None:
            raise SystemExit
        import json
        with open(aliases_file) as f:
            aliases = json.load(f)
    else:
        aliases = None

    # Configuration of the legend: appearance
    legend_conf = easygui.multenterbox(
        msg='Select configuration for the legend.\n\n- Decimals: 0 or positive integer for the number of decimals that '
            'the numbers of the legend should have if no `Legend aliases` was provided.\n\n- Colors used only: when com'
            'puting bins and thresholds, it is possible that some bins do not represent any country. Indicate "Yes" to '
            'omit these bins from the legend.\n\n- Text box: text to include on the map, like a title or a note. Leave '
            'blank if you do not wish any.',
        title='stats_mapper - Legend appearance configuration',
        fields=['Decimals:', 'Colors used only:', 'Text box:'],
        values=['0', 'Yes', '']
    )
    if legend_conf is None:
        raise SystemExit
    decimals, colors_used_only, text_box = legend_conf
    decimals = tools.str2num(decimals, int, 3)
    colors_used_only = tools.str2bool(colors_used_only)

else:
    # Configuration of the legend: appearance
    text_box = easygui.enterbox(
        msg='- Text box: text to include on the map, like a title or a note.\n   Leave blank if you do not wish any.',
        title='stats_mapper - Tex box',
        default=''
    )
    if text_box is None:
        raise SystemExit
    aliases, language, decimals, colors_used_only = None, None, None, None
text_box = text_box if text_box else None


# Draw the map
svg_map = draw_map(
    data=data,
    task=task,
    source_map=source_map,
    smart=smart,
    palette_style=palette_style,
    invert_palette=invert_palette,
    force_default_palette=force_default_palette,
    missing_color=missing,
    ocean_color=ocean,
    add_legend=add_legend,
    aliases=aliases,
    language=language,
    decimals=decimals,
    colors_used_only=colors_used_only,
    text_box=text_box
)

# Saving configuration
save_conf = easygui.multenterbox(
    msg='Select configuration for saving the map.\n\n- Bitmap: "Yes" to save the map as PNG, "No" to save the map as SV'
        'G.\n\n- DPI: dots per inch of the PNG if `Bitmap` is "Yes".\n\n- Width: width of the PNG if `Bitmap` is "Yes".'
        'Leave "auto" for automatic width.',
    title='stats_mapper - Saving configuration',
    fields=['Bitmap:', 'DPI:', 'Width:'],
    values=['Yes', '96', 'auto']
)
if save_conf is None:
    raise SystemExit
bitmap, dpi, width = save_conf
bitmap, dpi, width = tools.str2bool(bitmap), tools.str2num(dpi, int, 96), tools.str2num(width, int)


# Save map
out_map = easygui.filesavebox(
    msg='Save map',
    title='stats_mapper',
    default=os.path.join(*os.path.split(os.getcwd())[:-1], 'my_map'),
    filetypes=['*.png', 'PNG'] if bitmap else ['*.svg', 'SVG']
)
if out_map is None:
    raise SystemExit
files.save_map(
    svg_source_code=svg_map,
    path=out_map,
    bitmap=bitmap,
    dpi=dpi,
    width=width,
    overwrite=True
)
