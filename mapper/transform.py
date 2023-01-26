import numpy as np
import os
import json
import warnings
import re

from mapper.tools import (rounding, str2num, num2str, describe, interval_scale, str2color, input2palette,
                          map_coordinates, view_box, warnings_on_one_line, paragraph_center)


warnings.formatwarning = warnings_on_one_line  # Makes Python's `warnings.warn()` not mention itself


def make_thresholds(
        task: str,
        data: dict,
        smart_clean: bool = False
):
    """
    Calculates the thresholds and the default palette style to color the map from the data.

    :param task: (str) method for building the thresholds that determine the map coloring.
    :param data: (dict[*str: float]) data.
    :param smart_clean: (bool, default=False) whether to automatically remove the thresholds inconsistent with the data.
    :return: (tuple[list[*float], dict[*int: list[*str]]]) thresholds and intensities.
    """
    stats = describe(data)

    if task == 'values':
        task = f'b:{len(set(data.values()))}'
    if 'b:' in task:
        if stats['min'] == stats['max']:
            thresholds = []
        else:
            thresholds = list(np.linspace(stats['min'], stats['max'], str2num(task.split(':')[1], int) + 1))[1:-1]
    elif 't:' in task:
        thresholds = sorted([str2num(i, default=0.) for i in task.split(':')[1].replace(' ', '').split(',')])
    elif task == 'sign':
        thresholds = [0.]
    elif task in ['mean', 'average']:
        thresholds = [stats['mean']]
    elif task == 'median':
        thresholds = [stats['median']]
    elif task == 'std':
        mu = stats['mean']
        sigma = stats['std']
        thresholds = [mu - sigma, mu, mu + sigma]
    else:
        raise ValueError('`task` is not a valid value.')

    if smart_clean:
        thresholds = [i for i in thresholds if stats['min'] < i <= stats['max']]

    intensities_inverted = {key: interval_scale(val, thresholds) for key, val in data.items()}
    intensities = {val: [k for k, v in intensities_inverted.items() if v == val] for val in range(len(thresholds) + 1)}
    return thresholds, intensities


def build_seq_palette(
        n_items: int,
        c_map: str = 'Reds',
        str_out: bool = False

):
    """
    Builds a sequential palette of a primary RGB color for the specified number of colors.

    :param n_items: (int) number of colors tu use.
    :param c_map: (str) color palette.
    :param str_out: (bool, default=False) whether to return the color as a tuple of 3 integers or as a string
        containing "rgb({r},{g},{b})", where {r}, {g} and {b} stand for the RGB color components.
    :return: (list[*str] / list[*tuple[int, int, int]]) palette of RGB colors over 255.
    """
    palette = {
        'Reds': ['OrRd', 'Oranges', 'YlOrBr', 'Reds', 'RdPu', 'YlOrRd', 'PuRd'],
        'Greens': ['YlGn', 'Greens', 'YlGnBu', 'GnBu', 'Greys'],
        'Blues': ['PuBu', 'BuPu', 'Purples', 'Blues', 'PuBuGn', 'BuGn']
    }
    c_map_aux = ''
    for key, val in palette.items():
        if c_map in val:
            c_map_aux = key
            break
    if c_map_aux == 'Reds':
        r_max, r_min, r_param = 255, 100, 500
        g_max, g_min, g_param = 240, 0, 250
        b_max, b_min, b_param = 240, 0, 250
    elif c_map_aux == 'Greens':
        r_max, r_min, r_param = 240, 0, 250
        g_max, g_min, g_param = 255, 70, 350
        b_max, b_min, b_param = 250, 20, 250
    elif c_map_aux == 'Blues':
        r_max, r_min, r_param = 220, 0, 230
        g_max, g_min, g_param = 240, 50, 250
        b_max, b_min, b_param = 255, 100, 350
    else:
        raise ValueError(f'color palette {c_map} is not supported.')

    n = n_items if n_items >= 3 else 3
    reds = [min(r_max, rounding((i + 1) * (r_min - r_param) / n + r_param)) for i in range(n)][:n_items]
    greens = [min(g_max, rounding((i + 1) * (g_min - g_param) / n + g_param)) for i in range(n)][:n_items]
    blues = [min(b_max, rounding((i + 1) * (b_min - b_param) / n + b_param)) for i in range(n)][:n_items]
    seq_palette = list(zip(*[reds, greens, blues]))
    return ['rgb(' + ','.join(str(i) for i in rgb) + ')' for rgb in seq_palette] if str_out else seq_palette


def make_palette(
        palette_style: str,
        n_colors: int,
        smart: bool = True,
        invert_palette: bool = False,
        str_out: bool = True,
        force_default_palette: str = 'Reds'
):
    """
    Construct palette from the provided `palette_style`, based on the palette directive from http://colorbrewer2.org/.
        - If `palette_style` is in the directive of palettes:
            - If there are enough colors:
                + Assign that palette.
            - Else (if there are not enough colors):
                - If smart is on:
                    - If there is other palette of the same type ('seq', 'div', 'qual') with enough colors:
                        + Assign that palette instead.
                    - Else if the palette type is 'seq':
                        + Build palette with `build_seq_palette` function.
                    - Else (if there is no other palette of same type with enough colors and type is not 'seq'):
                        + Raise an error.
                - Else (if smart is off):
                    + Raise an error.
        - Else (if `palette_style` is not in the directive of palettes):
            - If it is a valid sequence of Hex or RGB colors:
                - If there are enough colors:
                    + Assign that palette.
                - Else (if there are not enough colors):
                    + Raise an error.
            - Else (if it is not a valid sequence of Hex or RGB colors):
                + Raise an error.

    :param palette_style: (str) palette name, or sequence of Hex and/or RGB colors separated by underscores.
    :param n_colors: (int) number of colors to use.
    :param smart: (bool, default=True) whether to use another palette if the requested one does not have enough colors.
    :param invert_palette: (bool, default=False) whether to use the palette colors with their order inverted.
    :param str_out: (bool, default=True) if `True`, return the palette as a list of 3-tuples of integers. If `False`,
        return the palette as a list of "rgb({r},{g},{b})" strings, being {r}, {g} and {b} the color components.
    :param force_default_palette: (str, default='Reds') if "Reds", "Greens" or "Blues" return a safe default palette
        of the given color if the provided `palette_style` makes the function fail for not being in the dictionary of
        palettes, for not having enough colors or for not being a valid sequence of Hex and/or RGB colors.
    :return: (list[*str] / list[*tuple[int, int, int]]) if `string_format` is `True`, return the palette as a list of
        3-tuples of integers representing the RGB color components. If `string_format` is `False`, return the palette
        as a list of "rgb({r},{g},{b})" strings, being {r}, {g} and {b} the RGB color components.
    """
    try:
        # Load palette directive
        with open(os.path.join(os.getcwd(), 'miscellaneous', 'colorbrewer.json'), 'r') as f:
            palette_dict = json.load(f)

        # Construct palette
        if palette_style in palette_dict.keys():
            try:
                palette = input2palette(palette_dict[palette_style][str(n_colors)], str_out)
            except KeyError:
                if smart:
                    if palette_dict[palette_style]['type'] == 'qual' and 3 <= n_colors <= 12:
                        palette = input2palette(palette_dict['Set3'][str(n_colors)], str_out)
                        warnings.warn(f'The palette style "{palette_style}" does not have {n_colors} colors. `smart` '
                                      f'parameter is on and the default qualitative palette "Set3" has been assigned.')
                    elif palette_dict[palette_style]['type'] == 'div' and 3 <= n_colors <= 11:
                        palette = input2palette(palette_dict['RdYlBu'][str(n_colors)], str_out)
                        warnings.warn(f'The palette style "{palette_style}" does not have {n_colors} colors. `smart` '
                                      f'parameter is on and the default divergent palette "RdYlBu" has been assigned.')
                    elif palette_dict[palette_style]['type'] == 'seq' and 3 <= n_colors <= 9:
                        palette = input2palette(palette_dict['YlGnBu'][str(n_colors)], str_out)
                        warnings.warn(f'The palette style "{palette_style}" does not have {n_colors} colors. `smart` '
                                      f'parameter is on and the default sequential palette "YlGnBu" has been assigned.')
                    else:
                        raise ValueError(f'The palette style "{palette_style}" does not have {n_colors} colors. '
                                         f'`smart` parameter is on and a default palette of the same type '
                                         f'"{palette_dict[palette_style]["type"]}" has been tried, but '
                                         f'it does not have enough colors either. Try less thresholds.')
                else:
                    raise ValueError(f'The palette style "{palette_style}" does not have {n_colors} colors. '
                                     f'Try other palette style or set `smart` parameter to `True`.')
        else:
            try:
                palette = input2palette(palette_style, str_out)
                if len(palette) < n_colors:
                    raise ValueError(f'The palette introduced does not have enough colors. Try less thresholds.')
            except ValueError as exception:
                if smart:
                    if 3 <= n_colors <= 11:
                        palette = input2palette(palette_dict['RdYlBu'][str(n_colors)], str_out)
                        warnings.warn(f'The palette style "{palette_style}" is not valid or does not '
                                      f'have {n_colors} colors. `smart` parameter is on and the '
                                      f'default divergent palette "RdYlBu" has been assigned.')
                    elif 3 <= n_colors <= 12:
                        palette = input2palette(palette_dict['Set3'][str(n_colors)], str_out)
                        warnings.warn(f'The palette style "{palette_style}" is not valid or does not '
                                      f'have {n_colors} colors. `smart` parameter is on and the '
                                      f'default qualitative palette "Set3" has been assigned.')
                    else:
                        raise ValueError(f'The palette style "{palette_style}" is not valid. `smart` '
                                         f'parameter is on and and a default palette has been tried, '
                                         f'but it does not have enough colors. Try less thresholds or '
                                         f'specify a prebuilt palette in `palette_style` parameter.')
                else:
                    raise exception

    except ValueError as exception:
        if force_default_palette in ['Reds', 'Greens', 'Blues']:
            palette = build_seq_palette(n_colors, force_default_palette, str_out)
            warnings.warn(f'A safe default sequential "{force_default_palette}" palette has '
                          f'been assigned because of the failure of the assignation of the '
                          f'requested palette due to the following exception:\n<<< {exception} >>>')
        else:
            raise ValueError(f'The assignation of the requested palette has failed due to the '
                             f'following exception:\n<<< {exception} >>>\nTry solving the error or specify '
                             f'the parameter `force_default_palette` as "Reds", "Greens" or "Blues".')

    # Invert palette if requested
    if invert_palette:
        palette = palette[::-1]

    return palette


def _css(
        intensities: dict,
        palette: list,
        country_list: list,
        missing_color: str = '#e6e6e6',
        ocean_color: str = '255,255,255',
        source_map: list = None
):
    """
    Writes the code for Cascading Style Sheet (CSS), which easily defines how countries are displayed in the SVG file.

    :param intensities: (dict[*int: list[*str]]) intensities of the countries, second element of the tuple output of
        function `make_thresholds`.
    :param palette: (list[*str]) palette of RGB colors over 255, output of function `make_palette`.
    :param country_list: (list[*str], default=None) list of the available countries in the map.
    :param missing_color: (str, default='#e6e6e6') color for the missing countries.
    :param ocean_color: (str, default='255,255,255') color for the oceans, seas and lakes.
    :param source_map: (list[*str], default=None) base map to use. Any combination of "africa", "antarctica", "asia",
        "europe", "north_america", "oceania", "south_america" and "world", followed or not followed each one by "*" to
        include intercontinental territories.
    :return: (str) code snippet with the CSS instructions.
    """
    maps = ['africa', 'antarctica', 'asia', 'europe', 'north_america', 'oceania', 'south_america']
    continents = ''
    if source_map is not None and 'world' not in source_map:
        source_map = [sm.lower() for sm in source_map if sm.replace('*', '') in maps]
        source_map_force = [sm.lower() for sm in source_map if '*' in sm and sm.replace('*', '') in maps]
        if source_map:
            continents += f'''{', '.join('.' + sm for sm in set(maps) - set(sm.replace('*', '') for sm in source_map))}
        {{
        opacity: 0;
        }}'''
        if source_map_force:
            continents += f'''
        {', '.join('.' + sm.replace('*', '') for sm in source_map_force)}
        {{
        opacity: 1;
        }}'''

    return '''
        /* Oval frame */
        .framexx
        {{
        fill: {ocean};
        opacity: {frame};
        }}

        /* Oceans, seas and lakes */
        .oceanxx
        {{
        opacity: 1;
        fill: {ocean};
        stroke: {ocean};
        stroke-width: 0.1;
        stroke-miterlimit: 1;
        }}

        /* Mainland */
        .landxx
        {{
        fill: {missing};
        stroke: #ffffff;
        stroke-width: 0.5;
        }}

        /* Small islands */
        .smallxx
        {{
        fill: {missing};
        stroke: #ffffff;
        stroke-width: 0.2;
        }}

        /* Land within a country */
        .inlandxx
        {{
        fill: {missing};
        fill-opacity: 0;
        }}

        /* Land with no borders */
        .coastxx
        {{
        fill: {missing};
        stroke: #ffffff;
        stroke-width: 0.2;
        }}

        /* Circles around small countries */
        .circlexx
        {{
        fill: {missing};
        fill-opacity: 0;
        }}

        /* Show continents */
        {show_continents}

        /* Color countries */
{color_countries}'''.format(
        missing=str2color(missing_color, True),
        ocean=str2color(ocean_color, True),
        show_continents=continents,
        frame=0 if source_map is None or 'world' in source_map else 1,
        color_countries=''.join(f'''        {", ".join(v for v in val if v in country_list)}
        {{
        fill: {palette[i]};
        fill-opacity: 1;
        }}
''' for i, (key, val) in enumerate(intensities.items()) if i == key and val and any(v in country_list for v in val))
    )


def _legend(
        thresholds: list,
        intensities: dict,
        palette: list,
        coordinates: dict,
        aliases: dict = None,
        language: str = 'math',
        decimals: int = 0,
        text_color: str = '0,0,0',
        colors_used_only: bool = True,
        highest_lowest: bool = False
):
    """
    Writes the code for the legend of an SVG map.

    :param thresholds: (list[*float]) thresholds that define in which bin each country is, first element of the tuple
    output of function `make_thresholds`.
    :param intensities: (dict[*int: list[*str]]) intensities of the countries, second element of the tuple output of
        function `make_thresholds`.
    :param palette: (list[*str]) palette of RGB colors over 255, output of function `make_palette`.
    :param coordinates: (dict[*str: int]) coordinates where the legend is to be in the image generated by the SVG file.
        Output of function `mapper.tools.map_coordinates`.
    :param aliases: (dict[*int: str], default=None) if `add_legend` evaluates to True, dictionary matching the keys in
        `intensities` with the provided descriptions to overwrite the automatic legend.
    :param language: (str, default='math') language to use for the legend.
    :param decimals: (int, default=0) number of decimals for the numbers in the legend.
    :param text_color: (str, default='0,0,0') color of the text of the legend.
    :param colors_used_only: (bool, default=True) whether to drop the bins where there are no countries represented.
    :param highest_lowest: (bool, default=False) whether to make the legend out of the minimum and maximum values only.
    :return: (str) code snippet of the legend.
    """
    scale = coordinates['scale']
    langs = {
        # á: &#225;
        # í: &#237;
        # less-than: &#60;
        # less-than or equal: &#8804;
        # greater-than: &#62;
        # greater-than or equal: &#8805;
        # en-dash &#8211;
        'en': {
            's-1': 'less than ',
            's-2': 'between ',
            's-3': ' and ',
            's-4': 'more than ',
            'hl': ['Lowest', 'Highest']
        },
        'es': {
            's-1': 'menos de ',
            's-2': 'entre ',
            's-3': ' y ',
            's-4': 'm&#225;s de ',
            'hl': ['M&#237;nimo', 'M&#225;ximo']
        },
        'de': {
            's-1': 'weniger als ',
            's-2': 'zwischen ',
            's-3': ' und ',
            's-4': 'mehr als ',
            'hl': ['Minimum', 'Maximal']
        },
        'math': {
            's-1': '&#60; ',
            's-2': '',
            's-3': ' &#8211; ',
            's-4': '&#8805; ',
            'hl': ['minimum', 'maximum']
        },
        'nerd': {
            's-1': 'x &#60; ',
            's-2': '',
            's-3': ' &#8804; x &#60; ',
            's-4': 'x &#8805; ',
            'hl': ['min(x)', 'max(x)']
        }
    }

    def rectangle(
            x: float,
            y: float,
            fill_color: str,
            stroke_color: str = '0,0,0'
    ):
        return f'<rect fill="{fill_color}" stroke="{stroke_color}" stroke-width="{scale * 1}" x="{x}" ' \
               f'y="{y}" width="{scale * 30}" height="{scale * 15}" rx="{scale * 5}" ry="{scale * 7}"/>'

    def text(
            x: float,
            y: float,
            content: str,
            color: str = '0,0,0'
    ):
        return f'<text x="{x}" y="{y}" fill="{color}" font-size="{scale * 15}px" class="textxx">{content}</text>'

    # Write the sentences
    if aliases is None:
        if highest_lowest:
            sentences = langs[language]['hl']
            palette_cuo = [palette[0], palette[-1]]
        else:
            sentences = [langs[language]['s-1'] + num2str(thresholds[0], decimals)] + [
                langs[language]['s-2'] + num2str(thresholds[i], decimals) +
                langs[language]['s-3'] + num2str(thresholds[i + 1], decimals)
                for i in range(len(thresholds) - 1)
            ] + [langs[language]['s-4'] + num2str(thresholds[-1], decimals)]
            # Drop the sentences and the colors that do not represent any country
            sentences = [sentences[key] for key, val in intensities.items() if val] if colors_used_only else sentences
            palette_cuo = [palette[key] for key, val in intensities.items() if val] if colors_used_only else palette
    else:
        sentences = list(list(zip(*sorted(aliases.items())))[1])
        palette_cuo = palette

    # Define the positions and their variations
    x_pos = coordinates['legend']['x']
    y_pos = coordinates['legend']['y']
    delta_x = scale * 37
    delta_y = scale * 13
    line_delta = -scale * 20

    # Return the legend code
    return '<g id="legend" class="legend">{}\n</g>'.format(''.join(
        f'''
    {rectangle(x_pos, y_pos + line_delta * i, palette_cuo[i], str2color(text_color, True))}
    {text(x_pos + delta_x, y_pos + delta_y + line_delta * i, sentences[i], str2color(text_color, True))}'''
        for i in range(len(palette_cuo))))


def _text_box(
        text: str,
        coordinates: dict,
        text_color: str = '0,0,0'
):
    """
    Writes the code for a text box in an SVG map.

    :param text: (str) text to display.
    :param coordinates: (dict[*str: int]) coordinates where the legend is to be in the image generated by the SVG file.
        Output of function `mapper.tools.map_coordinates`.
    :param text_color: (str, default='0,0,0') color of the text.
    :return: (str) code snippet of the text box.
    """
    font_size = coordinates['scale'] * 20
    line_width = rounding(
        (coordinates['limits']['x1'] - coordinates['limits']['x0']) / font_size, round_type='floor')
    x = rounding((coordinates['limits']['x1'] - coordinates['limits']['x0']) / 2 +
                 coordinates['limits']['x0'] - (line_width / 2 * font_size / 2), 3)
    y = rounding(coordinates['limits']['y1'] - font_size, 3)
    content = '\n'.join(f'        <tspan x="{x}" dy="{-font_size}">{p}</tspan>' for p in [
        ''.join([f'&#{ord(char)};' if re.match(r'[a-zA-Z0-9 ]', char) is None else char for char in line])
        for line in paragraph_center(text, line_width).split('\n')[::-1]
    ])
    return f'''<g id="text_box" class="text_box">
    <text x="{x}" y="{y + font_size}" fill="{str2color(text_color)}" font-size="{font_size}px" class="textxx">
{content}
    </text>
</g>'''


def build_svg(
        thresholds: list,
        intensities: dict,
        palette: list,
        source_map: list = None,
        missing_color: str = '#e6e6e6',
        ocean_color: str = '255,255,255',
        add_legend: int = 1,
        aliases: dict = None,
        language: str = 'math',
        decimals: int = 0,
        colors_used_only: bool = True,
        text_box: str = None
):
    """
    Writes the source code of the SVG file containing the requested map with the requested statistics of the countries.

    :param thresholds: (list[*float]) thresholds that define
    :param intensities: (dict[*int: list[*str]]) intensities of the countries, second element of the tuple output of
        function `make_thresholds`.
    :param palette: (list[*str]) palette of RGB colors over 255, output of function `make_palette`.
    :param source_map: (list[*str], default=None) base map to use. Any combination of "africa", "antarctica", "asia",
        "europe", "north_america", "oceania", "south_america" and "world", followed or not followed each one by "*" to
        include intercontinental territories.
    :param missing_color: (str, default='#e6e6e6') color for the missing countries.
    :param ocean_color: (str, default='255,255,255') color for the oceans, seas and lakes.
    :param add_legend: (int, default=1) if 0 do not add legend to the map, if 1 add automatic legend to the map, if 2
        add a highest-lowest legend to the map.
    :param aliases: (dict[*int: str], default=None) if `add_legend` evaluates to True, dictionary matching the
        keys in `intensities` with the provided descriptions to overwrite the automatic legend.
    :param language: (str, default='math') if `add_legend` evaluates to True, language to use for the legend.
    :param decimals: (int, default=0) if `add_legend` is 1, number of decimals for the numbers in the legend.
    :param colors_used_only: (bool, default=True) if `add_legend` is 1, whether to drop from the legend the color
        bins that do not represent any country.
    :param text_box: (str, default=None) text to display on the map if provided.
    :return: (str) SVG source code.
    """
    # Get map name and the coordinates where the legend is to be
    coordinates = map_coordinates(source_map, bool(add_legend), False if text_box is None else bool(text_box))

    # Load empty map and prepare the SVG sections
    with open(os.path.join(os.getcwd(), 'maps', 'World.svg'), 'r') as f:
        empty_map = f.read()
    svg_intro = empty_map.split('<style type="text/css">')[0] + '<style type="text/css">{css}    </style>\n</defs>'
    svg_body = empty_map.split('</defs>')[1].replace('</svg>', '') + '{legend}{text}\n</svg>'
    country_list = ['.' + element[:2].lower() for element in svg_body.split('\n<g id="')][1:-1]

    # Legend is going on the ocean. The color of the text depends on how dark the ocean is
    text_color = '0,0,0' if sum([c * t for c, t in zip([0.299, 0.587, 0.114], str2color(ocean_color))]) > 186 \
        else '255,255,255'

    # Make CSS
    css = _css(
        intensities=intensities,
        palette=palette,
        country_list=country_list,
        missing_color=missing_color,
        ocean_color=ocean_color,
        source_map=source_map
    )

    # Make legend
    legend = _legend(
        thresholds=thresholds,
        intensities=intensities,
        palette=palette,
        coordinates=coordinates,
        aliases=aliases,
        language=language,
        decimals=decimals,
        text_color=text_color,
        colors_used_only=colors_used_only,
        highest_lowest=True if add_legend == 2 else False
    ) if add_legend else ''

    # Add text box
    text = _text_box(
        text=text_box,
        coordinates=coordinates,
        text_color=text_color
    ) if text_box is not None else ''

    # Fill, join and return the SVG sections
    return re.sub(r'width="\d+\.*\d*" height="\d+\.*\d*" viewBox="(\d+\.*\d*\s){3}\d+\.*\d*"',
                  view_box(coordinates['limits']), svg_intro.format(css=css)
                  ) + svg_body.format(legend=legend, text=('\n' if legend and text else '') + text)
