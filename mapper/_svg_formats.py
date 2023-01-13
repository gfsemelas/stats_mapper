import os
import pandas as pd
import re
from svgpathtools import svg2paths, Path
from io import StringIO

from .tools import rounding


def _svg4css(
        svg_in: str = os.path.join(os.getcwd(), 'maps', 'world-states.svg'),
        svg_out: str = os.path.join(os.getcwd(), 'maps', 'World.svg')
):
    """
    Formats a world SVG so it can be used by the project stats_mapper.

    :param svg_in: (str, default='./maps/world-states.svg') source SVG.
    :param svg_out: (str, default='./maps/World.svg') SVG ready for use by the project stats_mapper.
    """
    countries = pd.read_csv(
        os.path.join(os.getcwd(), 'miscellaneous', 'isoalpha.csv'), sep=';', encoding='latin_1', na_filter=False)
    continents = ''

    with open(svg_in, encoding='latin_1') as f:
        empty_map = f.read()

    empty_map = empty_map.replace(
        '<![CDATA[ text { cursor: default; } ]]>',
        '''
        /* Oval frame */
        .framexx
        {
        fill: #ffffff;
        opacity: 0;
        }

        /* Oceans, seas and lakes */
        .oceanxx
        {
        opacity: 1;
        fill: #ffffff;
        stroke: #ffffff;
        stroke-width: 0.1;
        stroke-miterlimit: 1;
        }

        /* Mainland */
        .landxx
        {
        fill: #e0e0e0;
        stroke: #ffffff;
        stroke-width: 0.5;
        }

        /* Small islands */
        .smallxx
        {
        fill: #e0e0e0;
        stroke: #ffffff;
        stroke-width: 0.2;
        }

        /* Land within a country */
        .inlandxx
        {
        fill: #e0e0e0;
        fill-opacity: 0;
        }

        /* Islands with no borders */
        .coastxx
        {
        fill: #e0e0e0;
        stroke: #ffffff;
        stroke-width: 0.2;
        }

        /* Circles around small countries */
        .circlexx
        {
        fill: #e0e0e0;
        fill-opacity: 0;
        }
    '''
    )

    new_lines = []
    ids = []
    for line in empty_map.split('\n'):
        framexx = re.match(r'\s*<rect id="(.+?)" x="0" y="0" fill="#\w{6}"', line)
        oceanxx = re.match(r'\s*<path id="(.*?[oO][cC][eE][aA][nN].*?)" fill="#\w{6}" stroke="#\w{6}" '
                           r'stroke-width="0\.1" stroke-miterlimit="1"', line)
        gid = re.match(r'\s*<g id="(.+)">', line)
        gend = re.match(r'\s*</g>', line)
        landxx = re.match(r'\s*<path id="(.+?)" fill="#\w{6}" stroke="#\w{6}" stroke-width="0\.5"', line)
        smallxx = re.match(r'\s*<circle id="(.+?)" fill="#\w{6}" stroke="#\w{6}" stroke-width="0\.2"', line)
        coastxx = re.match(r'\s*<path id="(.+?)" fill="#\w{6}" stroke="#\w{6}" stroke-width="0\.2"', line)
        inlandxx = re.match(r'\s*<path id="(.+?)" fill="#\w{6}" fill-opacity="0"', line)
        circlexx = re.match(r'\s*<circle id="(.+?)" fill="#\w{6}" fill-opacity="0"', line)

        # Check if line represents the frame
        if framexx is not None:
            current_id = framexx.group(1)
            new_lines.append(re.sub(
                r'<rect id=".+?" x="0" y="0" fill="#\w{6}"',
                f'<rect class="framexx" id="{current_id}" x="0" y="0"',
                line
            ))

        # Check if line represents the ocean
        elif oceanxx is not None:
            current_id = oceanxx.group(1)
            new_lines.append(re.sub(
                r'<path id=".*?[oO][cC][eE][aA][nN].*?" fill="#\w{6}" stroke="#\w{6}" '
                r'stroke-width="0\.1" stroke-miterlimit="1"',
                f'<path class="oceanxx" id="{current_id}"',
                line
            ))

        # Check if line is the beginning of a group and get its id
        elif gid is not None:
            if gid.group(1).upper() in countries['ALPHA_2'].values:
                continents = " ".join(countries[countries['ALPHA_2'] == gid.group(1).upper()]['CONTINENT'].item(
                    ).lower().replace(' ', '_').split('|'))
                continents = continents + ' ' if continents else ''
            ids += [gid.group(1).lower()]
            new_lines.append(line)

        # Check if a line is the end of a group and remove the last id
        elif gend is not None:
            ids.pop()
            new_lines.append(line)

        # Check if line represents a path of a mainland
        elif landxx is not None:
            current_id = landxx.group(1)
            new_lines.append(re.sub(
                r'<path id=".+?" fill="#\w{6}" stroke="#\w{6}" stroke-width="0\.5"',
                f'<path class="landxx {continents}{" ".join(ids)}" id="{current_id}"',
                line
            ))

        # Check if line represents a really small island
        elif smallxx is not None:
            current_id = smallxx.group(1)
            new_lines.append(re.sub(
                r'<circle id=".+?" fill="#\w{6}" stroke="#\w{6}" stroke-width="0\.2"',
                f'<circle class="smallxx {continents}{" ".join(ids)}" id="{current_id}"',
                line
            ))

        # Check if line represents a path of a coast
        elif coastxx is not None:
            current_id = coastxx.group(1)
            new_lines.append(re.sub(
                r'<path id=".+?" fill="#\w{6}" stroke="#\w{6}" stroke-width="0\.2"',
                f'<path class="coastxx {continents}{" ".join(ids)}" id="{current_id}"',
                line
            ))

        # Check if line represents a path of land within a country
        elif inlandxx is not None:
            current_id = inlandxx.group(1)
            new_lines.append(re.sub(
                r'<path id=".+?" fill="#\w{6}" fill-opacity="0"',
                f'<path class="inlandxx {continents}{" ".join(ids)}" id="{current_id}"',
                line
            ))

        # Check if line represents a circle
        elif circlexx is not None:
            current_id = circlexx.group(1)
            new_lines.append(re.sub(
                r'<circle id=".+?" fill="#\w{6}" fill-opacity="0"',
                f'<circle class="circlexx {continents}{" ".join(ids)}" id="{current_id}"',
                line
            ))

        else:
            new_lines.append(line)

    new_empty_map = '\n'.join(new_lines)
    with open(svg_out, 'w', encoding='latin_1') as f:
        f.write(new_empty_map)


def _countries_bbox(
        svg_in: str = os.path.join(os.getcwd(), 'maps', 'world-states.svg')
):
    """
    Finds the bounding box coordinates for all countries in the SVG.

    :param svg_in: (str, default='./maps/world-states.svg') source SVG.
    :return: (dict[*str: dict[*str: dict[str: float, str: float, str: float, str: float]]]) bounding box coordinates
        for all countries in the SVG file by continent.
    """
    with open(svg_in) as f:
        svg = f.read()

    frame = '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.or' \
            'g/Graphics/SVG/1.1/DTD/svg11.dtd">\n<svg version="1.1"\n    id="Earth" xmlns:dc="http://purl.org/dc/elem' \
            'ents/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-' \
            'ns#" xmlns:svg="http://www.w3.org/2000/svg"\n    xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://' \
            'www.w3.org/1999/xlink" x="0px" y="0px" width="1690" height="1735.37" viewBox="414 3.732 169 173.537" xml' \
            ':space="preserve">\n<defs><style type="text/css"><![CDATA[ text {{ cursor: default; }} ]]></style></defs' \
            '>\n{}\n</svg>'

    isoalpha = pd.read_csv('miscellaneous/isoalpha.csv', sep=';', encoding='latin_1', na_filter=False)
    countries = {
        continent: {
            c: f'\n<g id="{c}">' + svg.split(f'\n<g id="{c}">')[1].split('\n</g>')[0] + '\n</g>'
            for c in sorted(isoalpha[isoalpha['CONTINENT'] == continent]['ALPHA_2']) if f'\n<g id="{c}">' in svg
        } for continent in sorted(isoalpha['CONTINENT'].unique())
    }

    coordinates = {}
    for continent, country_list in countries.items():
        coordinates[continent] = {}
        for country, borders in country_list.items():
            paths, _ = svg2paths(StringIO(frame.format(countries[continent][country])))
            complete_path = Path(*[segment for p in paths for segment in p._segments])
            x0, x1, y0, y1 = complete_path.bbox()
            x0_circle, y0_circle, x1_circle, y1_circle = float('inf'), float('inf'), -float('inf'), -float('inf')
            for cx, cy, r in re.findall(r'<circle class=".+?" id="\w+?" cx="([0-9.]+)" cy="([0-9.]+?)" r="([0-9.]+)"/>',
                                        countries[continent][country]):
                x0_circle = min(x0_circle, float(cx) - float(r))
                y0_circle = min(y0_circle, float(cy) - float(r))
                x1_circle = max(x1_circle, float(cx) + float(r))
                y1_circle = max(y1_circle, float(cy) + float(r))
            coordinates[continent][country] = {
                'x0': rounding(min(x0, x0_circle), round_type='floor', decimals=3),
                'y0': rounding(min(y0, y0_circle), round_type='floor', decimals=3),
                'x1': rounding(max(x1, x1_circle), round_type='ceil', decimals=3),
                'y1': rounding(max(y1, y1_circle), round_type='ceil', decimals=3)
            }
    # Run the following commented lines to find the bounding box coordinates of the full continent
    # cont = CONTINENT
    # continent = bboxes[cont.replace('_', ' ').title()]
    # x0 = min([str2float(val['x0'], round_type='floor', decimals=3) for c, val in continent.items()])
    # y0 = min([str2float(val['y0'], round_type='floor', decimals=3) for c, val in continent.items()])
    # x1 = max([str2float(val['x1'], round_type='ceil', decimals=3) for c, val in continent.items()])
    # y1 = max([str2float(val['y1'], round_type='ceil', decimals=3) for c, val in continent.items()])
    # print(f"'x0': {x0},  # {[c for c, val in continent.items() if val['x0'] == x0][0]}")
    # print(f"'y0': {y0},  # {[c for c, val in continent.items() if val['y0'] == y0][0]}")
    # print(f"'x1': {x1},  # {[c for c, val in continent.items() if val['x1'] == x1][0]}")
    # print(f"'y1': {y1}  # {[c for c, val in continent.items() if val['y1'] == y1][0]}")
    return coordinates
