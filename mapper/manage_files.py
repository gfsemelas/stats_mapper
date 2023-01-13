import pandas as pd
import os
import re

from mapper.tools import str2num


def file_fields(
        file: str
):
    """
    Returns the directory, the name and the extension of a file separately.

    :param file: (str) identification of the file.
    :return: (tuple[str, str, str]) directory, name and extension of the file.
    """
    dir_sep = os.path.split(file)
    directory = os.path.join(*dir_sep[:-1])
    file = dir_sep[-1]
    if '.' in file:
        dot_sep = file.split('.')
        name = '.'.join(dot_sep[:-1])
        ext = '.' + dot_sep[-1]
    else:
        name = file
        ext = ''
    return directory, name, ext.lower()


def get_file_names(
        directory: str = '.',
        which: str = 'archives'
):
    """
    Gets the file names in the provided directory.

    :param directory: (str, default='.') path.
    :param which: (str, default='archives') 'folders' or 'archives' to return all folder or archive names, respectively.
    :return: (list[*str]) list of folders or list of archives.
    """
    index = 1 if which == 'folders' else 2
    return next(os.walk(directory), (None, None, []))[index]


def load_csv(
        file,
        sep: str = ','
):
    """
    Loads the data of a CSV.

    :param file: (str) name of the CSV file with the data to load.
    :param sep: (str, default=',') CSV separator character.
    :return: (pandas.DataFrame) data.
    """
    # Read file
    data = pd.read_csv(file, sep=sep, header=None, encoding='latin_1', dtype=str, na_filter=False)

    # Get list of possible countries
    with open(os.path.join(os.getcwd(), 'maps', 'World.svg')) as f:
        countries_svg = set(re.findall(r'<g id="([A-Z]+)">', f.read()))
    countries = pd.read_csv(
        os.path.join(os.getcwd(), 'miscellaneous', 'isoalpha.csv'), sep=';', encoding='latin_1', na_filter=False)
    countries = countries[countries['ALPHA_2'].isin(countries_svg)]['ALPHA_2'].tolist()

    # Format and drop NaNs
    data[0] = data[0].apply(
        lambda x: '.' + x.strip().lower() if x.strip().upper() in countries else float('nan'))
    data[1] = data[1].apply(str2num)
    data = data.dropna()
    return dict(zip(data[0], data[1]))


def load_sheet(
        file,
        sheet: str = 'Sheet1',
        country_col: str = 'COUNTRY',
        data_col: str = 'DATA'
):
    """
    Loads the data of a spreadsheet.

    :param file: (str) name of the file with the data to load.
    :param sheet: (str, default='Sheet1') name of the sheet where the data are.
    :param data_col: (str, default='COUNTRY') name of the column where the countries are.
    :param country_col: (str, default='DATA') name of the column where the numeric data are.
    :return: (pandas.DataFrame) data.
    """
    # Read file
    data = pd.read_excel(file, sheet_name=sheet, converters={country_col: str, data_col: str}, keep_default_na=False)

    # Get list of possible countries
    with open(os.path.join(os.getcwd(), 'maps', 'World.svg')) as f:
        countries_svg = set(re.findall(r'<g id="([A-Z]+)">', f.read()))
    countries = pd.read_csv(
        os.path.join(os.getcwd(), 'miscellaneous', 'isoalpha.csv'), sep=';', encoding='latin_1', na_filter=False)
    countries = countries[countries['ALPHA_2'].isin(countries_svg)]['ALPHA_2'].tolist()

    # Format and drop NaNs
    data[country_col] = data[country_col].apply(
        lambda x: '.' + x.strip().lower() if x.strip().upper() in countries else float('nan'))
    data[data_col] = data[data_col].apply(str2num)
    data = data[[country_col, data_col]].dropna()
    return dict(zip(data[country_col], data[data_col]))


def save_map(
        svg_source_code: str,
        path: str = None,
        bitmap: bool = True,
        dpi: int = 96,
        width: int = None,
        overwrite: bool = False
):
    """
    Saves the SVG source code of a map as an SVG file or PNG file.

    :param svg_source_code: (str) SVG source code.
    :param path: (str, default=None) full path where to save the file. If None, the file is saved with the name "my_map"
        and the extension requested with the parameter `bitmap` in the same directory as the stats_map project.
    :param bitmap: (bool, default=True) if True, save the map as PNG, else as SVG.
    :param dpi: (int, default=96) DPIs of the PNG if `bitmap` is True.
    :param width: (int, default=None) width in pixels of the PNG if `bitmap` is True. If None, width is automatic.
    :param overwrite: (bool, default=False) whether to overwrite a map if it already exists with the same path.
    """
    fpath, fname, fext = file_fields(path)
    if path is None:
        file_name = 'my_map{}'
        path = os.path.join(*os.path.split(os.getcwd())[:-1])
    elif not fpath:
        file_name = fname + '{}'
        path = os.path.join(*os.path.split(os.getcwd())[:-1])
    elif not fname:
        file_name = 'my_map{}'
    else:
        file_name = fname + '{}'
        path = fpath

    existing_file_names = [file_fields(f)[1] for f in get_file_names(path)]
    i = 0
    template = ''
    while file_name.format(template) in existing_file_names and not overwrite:
        i += 1
        template = f' ({i})'
    path = os.path.join(path, file_name.format(template)) + (fext if fext else ('.png' if bitmap else '.svg'))

    if bitmap:
        from cairosvg import svg2png
        svg2png(bytestring=svg_source_code, write_to=path, dpi=dpi, output_width=None if pd.isna(width) else width)
    else:
        with open(path, 'w') as f:
            f.write(svg_source_code)
