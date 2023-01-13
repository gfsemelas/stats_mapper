import numpy as np
import re
import pandas as pd
from itertools import product


def str2bool(
        val: str
):
    """
    Convert a string representation of truth to true (1) or false (0). True values are 'y', 'yes', 't', 'true', 'on',
    and '1'; false values are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if 'val' is anything else.

    :param val: (str) word.
    :return: (int) 0 if ```val``` represents a truth value of false or 1 if ```val``` represents a truth value of true.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError("invalid truth value %r" % (val,))


def rounding(
        n: (float, int),
        decimals: int = 0,
        round_type: str = 'round'
):
    """
    Rounds a number.

    :param n: (float / int) number to round.
    :param decimals: (int, default=0) round to this number of decimals. If None, no rounding is applied.
    :param round_type: (str, default='round') 'round', 'ceil' or 'floor' for the type of rounding.
    :return: (float / int) number rounded.
    """
    if decimals is None:
        return n
    elif isinstance(decimals, int) and decimals >= 0:
        if round_type == 'round':
            return round(n, decimals) if decimals else round(n)
        else:
            n *= 10 ** decimals
            r = (int(n) + int(bool(n - int(n))) * {'ceil': 1, 'floor': 0}[round_type]) / 10 ** decimals
            return r if decimals else int(r)
    else:
        raise ValueError('Parameter decimals must be "None", 0 or a positive integer.')


def str2num(
        number: str,
        dtype: type = None,
        default: float = float('nan')
):
    """
    Converts a string with or without suffix into a number.
    Available suffixes are 'm' for milli, 'K' for kilo, 'M' for mega, 'G' for giga, etc.

    :param number: (str) number in string format, with or without a suffix.
    :param dtype: (type, default=None) int or float instances. Type of the desired output. If None, the output is
        converted to float if `number` has a point and to integer otherwise.
    :param default: (Any, default=float('nan')) default value to return if the conversion raises a ValueError.
    :return: (int / float) string converted to number if it was possible to do so, or the default value otherwise.
    """
    number = number.strip()
    if not number:
        return default
    magnitudes = {
        'q': 1e-30,
        'r': 1e-27,
        'y': 1e-24,
        'z': 1e-21,
        'a': 1e-18,
        'f': 1e-15,
        'p': 1e-12,
        'n': 1e-9,
        '\u03BC': 1e-6,
        'm': 1e-3,
        'k': 1e3,
        'K': 1e3,
        'M': 1e6,
        'G': 1e9,
        'T': 1e12,
        'P': 1e15,
        'E': 1e18,
        'Z': 1e21,
        'Y': 1e24,
        'R': 1e27,
        'Q': 1e30
    }
    dtype = dtype if dtype is not None else \
        (float if '.' in number or (not number.isdigit() and number[-1].islower() and number[-1] != 'k') else int)
    if dtype in [int, float]:
        if number.replace('.', '').isdigit():
            return dtype(float(number))
        elif number[-1] in magnitudes and number[:-1].replace('.', '').isdigit():
            return dtype(float(number[:-1]) * magnitudes[number[-1]])
        else:
            return default
    else:
        raise ValueError(f'Possible values for `dtype` parameter are "{int}", '
                         f'"{float}" or "{type(None)}", but it was {dtype}.')


def num2str(
        number: (int, float),
        precision: int = 0
):
    """
    Converts a number into a number with suffix in string format.
    Available suffixes are 'm' for milli, 'K' for kilo, 'M' for mega, 'G' for giga, etc.

    :param number: (int / float) number to convert to string with suffix if appropriate.
    :param precision: (int, default=0) number of decimals desired in the output.
    :return: (str) number provided as a string.
    """
    if number is None or number == float('inf') or pd.isna(number):
        return str(number)

    def distance(e, m):
        if (e >= 0 and e - m >= 0) or (e <= 0 and e - m <= 0):
            return abs(e - m)
        return float('inf')

    magnitudes = {
        -30: 'q',
        -27: 'r',
        -24: 'y',
        -21: 'z',
        -18: 'a',
        -15: 'f',
        -12: 'p',
        -9: 'n',
        -6: '\u03BC',
        -3: 'm',
        0: '',
        3: 'k',
        6: 'M',
        9: 'G',
        12: 'T',
        15: 'P',
        18: 'E',
        21: 'Z',
        24: 'Y',
        27: 'R',
        30: 'Q',
    }

    sci = f'{number:.{len(str(number))}e}'
    num, exp = float(sci[:-4]), int(sci[-3:])
    mags = list(magnitudes.keys())
    mags_exp_distance = [distance(exp, mag) for mag in mags]
    app_mag = mags[mags_exp_distance.index(min(mags_exp_distance))]
    num_mag = str(rounding(num * (10 ** (exp - app_mag)), precision))
    if precision == 0 or int(num_mag.split('.')[-1]) == 0:
        num_mag = num_mag.split('.')[0]

    return num_mag + magnitudes[app_mag]


def describe(
        data: dict
):
    """
    Calculates basic statistics of the data.

    :param data: (dict[*str: float]) data.
    :return: (dict[str: int, *str: float]) statistics.
    """
    d = list(data.values())
    return {
        'count': len(d),
        'max': max(d),
        'min': min(d),
        'mean': np.mean(d),
        'std': np.std(d)
    }


def interval_scale(
        n: (int, float),
        intervals: list
):
    """
    Returns in which interval of `intervals` is the number `n`.

    :param n: (int / float) number.
    :param intervals: (list) sequence with the limits of the intervals.
    :return: (int) nth interval of `intervals` in which `n` is.
    """
    r = 0
    for i in sorted(intervals):
        if n >= i:
            r += 1
        else:
            break
    return r


def str2color(
        color: str,
        str_out: bool = False
):
    """
    Converts a string representing a color in Hex or RGB into a 3-tuple representing RGB in the 0-255 scale.

    :param color: (str) Hex or RGB color.
    :param str_out: (bool, default=False) whether to return the color as a tuple of 3 integers or as a string
        containing "rgb({r},{g},{b})", where {r}, {g} and {b} stand for the RGB color components.
    :return: (str / tuple[int, int, int]) RGB color in the 0-255 scale.
    """
    hex_pattern = re.compile(r'.*?([a-z0-9]{6})')
    rgb255_pattern = re.compile(r'.*?(\d{1,3})\D+(\d{1,3})\D+(\d{1,3})')
    rgb1_pattern = re.compile(r'.*?(0?\.\d*)\D+(0?\.\d*)\D+(0?\.\d*)')

    hex_match = hex_pattern.match(color.lower())
    rgb255_match = rgb255_pattern.match(color)
    rgb1_match = rgb1_pattern.match(color)

    if hex_match is not None:
        rgb = tuple([int(hex_match.group(1)[i:i + 2], 16) for i in range(0, 6, 2)])
    elif rgb255_match is not None:
        rgb = tuple([int(i) for i in rgb255_match.groups()])
    elif rgb1_match is not None:
        rgb = tuple([rounding(float(i) * 255) for i in rgb1_match.groups()])
    else:
        rgb = [float('nan')]

    if all(0 <= c <= 255 for c in rgb):
        return 'rgb(' + ','.join(str(i) for i in rgb) + ')' if str_out else rgb
    else:
        raise ValueError(f'Color formatting "{color}" is neither Hex nor RGB.')


def input2palette(
        inp: (str, list),
        str_out: bool = False
):
    """
    Converts a list or a string representing a sequence of colors in Hex and/or RGB formats into a palette, where a
    palette is a list of RGB colors, where an RGB color is a tuple of 3 integers in the 0-255 scale.

    :param inp: (str / list) sequence of Hex and/or 3-tuple RGB colors, separated by underscores if sequence is string.
    :param str_out: (bool, default=False) whether to return the colors as tuples of 3 integers or as strings
        containing "rgb({r},{g},{b})", where {r}, {g} and {b} stand for the RGB color components.
    :return: (list[*str] / list[*tuple[int, int, int]]) palette of RGB colors over 255.
    """
    if not isinstance(inp, list):
        inp = inp.split('_')
    try:
        return [str2color(c, str_out) for c in inp]
    except ValueError:
        raise ValueError(f'Color palette "{inp}" is not valid.')


def add_margins(
        coordinates: dict,
        add: (float, int) = 10,
        limits: dict = None
):
    """
    From the coordinates of the top left (x0, y0) and bottom right (x1, y1) corners of an object, computes its width
    and height and adds a proportional margin on each side of them.

    :param coordinates: (dict['x0': float, 'y0': float, 'x1': float, 'y1': float]) coordinates of the top left (x0, y0)
        and bottom right (x1, y1) corners of the object to add margins to.
    :param add: (float / int) quantity to add as margins.
    :param limits: (dict[*str: float], default=None) indicate the limits that the margins cannot trespass, if exist.
    :return: (dict['x0': float, 'y0': float, 'x1': float, 'y1': float]) coordinates of the top left (x0, y0) and bottom
        right (x1, y1) corners of the object with the margins added.
    """
    limits = limits if isinstance(limits, dict) else {}
    for x in ['x0', 'y0', 'x1', 'y1']:
        limits[x] = float('nan') if limits.get(x) is None else limits[x]
    if limits['x1'] <= limits['x0'] or limits['y1'] <= limits['y0']:
        raise ValueError('No negative or zero distances are allowed. Ensure that x1 > x0 and y1 > y0.')
    width = coordinates['x1'] - coordinates['x0']
    height = coordinates['y1'] - coordinates['y0']
    wratio, hratio = (width / height, 1) if width > height else (1, height / width)
    return {
        'x0': max(rounding(coordinates['x0'] - add * wratio, 3, 'floor'), limits['x0']),
        'y0': max(rounding(coordinates['y0'] - add * hratio, 3, 'floor'), limits['y0']),
        'x1': min(rounding(coordinates['x1'] + add * wratio, 3, 'ceil'), limits['x1']),
        'y1': min(rounding(coordinates['y1'] + add * hratio, 3, 'ceil'), limits['y1'])
    }


def map_coordinates(
        source_map: list = None,
        add_legend: bool = False,
        add_textbox: bool = False
):
    """
    Gives the coordinates of the SVG where the legend and text box should go, and the coordinates for cropping the PNG.

    :param source_map: (list[*str], default=None) base map to use. Any combination of "africa", "antarctica", "asia",
        "europe", "north_america", "oceania", "south_america" and "world", followed or not followed each one by "*" to
        include intercontinental territories.
    :param add_legend: (bool, default=False) whether a legend is to be added (increases the limits).
    :param add_textbox: (bool, default=False) whether a text box is to be added (increases the limits).
    :return: (dict[*str: list[*float]]) coordinates.
    """
    limits = {
        'africa': {
            'x0': 403.011,  # CV
            'y0': 136.133,  # TN
            'x1': 630.677,  # MU
            'y1': 362.914  # ZA
        },
        'antarctica': {
            'x0': 194.460,  # AQ
            'y0': 405.910,  # TF
            'x1': 818.338,  # AQ
            'y1': 507.134  # AQ
        },
        'asia': {
            'x0': 564.185,  # PS
            'y0': 86.178,  # CN
            'x1': 863.661,  # ID
            'y1': 287.894  # ID
        },
        'asia*': {
            'x0': 522.679,  # RU
            'y0': 11.54,  # RU
            'x1': 876.918,  # RU
            'y1': 287.894  # ID
        },
        'europe': {
            # 'x0': 283.263,  # NL
            'x0': 399.800,  # PT
            'y0': 13.748,  # NO
            'x1': 573.056,  # UA
            # 'y1': 217.852  # NL
            'y1': 166.599  # SP
        },
        'europe*': {
            # 'x0': 283.263,  # NL
            'x0': 399.800,  # PT
            'y0': 11.540,  # RU
            # 'x1': 876.918,  # RU
            # 'x1': 687.464,  # KZ
            'x1': 603.163,  # AZ
            # 'y1': 217.852  # NL
            'y1': 166.599  # SP
        },
        'north_america': {
            'x0': 36.947,  # US
            'y0': 8.303,  # GL
            # 'x1': 924.110,  # US
            'x1': 462.990,  # GL
            'y1': 236.687  # CR
        },
        'oceania': {
            #  'x0': 9.811,  # CK
            'x0': 775.712,  # AU
            'y0': 203.210,  # MP
            'x1': 996.932,  # TK
            'y1': 422.850  # AU
        },
        'south_america': {
            'x0': 179.160,  # CL
            'y0': 214.463,  # CO
            'x1': 375.768,  # BR
            'y1': 427.896  # CL
        },
        'world': {
            'x0': 0,
            'x1': 1000,
            'y0': 0,
            'y1': 507.209
        }
    }

    if source_map is None or 'world' in source_map:
        coordinates_limits = limits['world']
        coordinates_legend = {'x': 80, 'y': 400}
    else:
        coordinates_limits = {
            c: limits[continent][c] for c in ['x0', 'x1', 'y0', 'y1']
            for continent in pd.DataFrame.from_dict(limits).T.drop('world').sort_values(c, ascending=int(c[1])).index
            if continent in [m if m in ['europe*', 'asia*'] else m.replace('*', '') for m in source_map]
        }
        coordinates_legend = {
            'x': max(limits['world']['x0'] + 80, coordinates_limits['x0'] - 20),
            'y': min(limits['world']['y1'] - 100, coordinates_limits['y1'] - 20)
        }
        if add_legend:
            coordinates_limits['x0'] = min(coordinates_limits['x0'], coordinates_legend['x'])
            coordinates_limits['y1'] = max(coordinates_limits['y1'], coordinates_legend['y'])
        if add_textbox:
            coordinates_limits['y1'] = min(limits['world']['y1'], coordinates_limits['y1'] + 60 *
                                           rounding((coordinates_limits['y1'] - coordinates_limits['y0']) /
                                                    (limits['world']['y1'] - limits['world']['y0']), 3))
        coordinates_limits = add_margins(coordinates_limits, limits=limits['world'])

    coordinates = {
        'world': limits['world'],
        'limits': coordinates_limits,
        'legend': coordinates_legend,
        'scale': rounding((coordinates_limits['y1'] - coordinates_limits['y0']) /
                          (limits['world']['y1'] - limits['world']['y0']), 3)
    }
    return coordinates


def paragraph_center(
        text: str,
        line_width: int = 128,
        n_lines: int = None
):
    """
    Formats a text into a centered paragraph whose lines have the most similar number of characters. To divide this
    lines, the function takes as input the maximum line width possible or the desired number of lines.

    :param text: (str) text to format into a centered paragraph.
    :param line_width: (int, default=128) maximum line width possible.
    :param n_lines: (int, default=None) desired number of lines. If provided, it overrides `line_width`.
    :return: (str) text formatted into a centered paragraph.
    """
    if not isinstance(n_lines, int):
        if isinstance(line_width, int):
            n_lines = rounding(len(text) / line_width, round_type='ceil')
        else:
            raise ValueError('At least one of `line_width` and `n_rows` must be an integer.')
    if n_lines < 2:
        return text
    words = text.split()
    mean_words_per_line = len(words) / n_lines
    margin = 5
    possible_cuts = [[0] + [1] * len(words)] + [
        [0] + list(c) for c in product(
            range(max(1, rounding(mean_words_per_line, round_type='floor') - margin),
                  min(rounding(mean_words_per_line, round_type='ceil') + margin,
                      max(len(words) - n_lines, rounding(len(text) / n_lines, round_type='floor')))),
            repeat=n_lines
        ) if sum(c) == len(words)
    ]
    possible_lengths = [
        [len(' '.join(words[sum(c[:i]):sum(c[:i+1])])) for i in range(1, len(c))]
        for c in possible_cuts
    ]
    metrics = [sum([abs(i - j) for i in c for j in c]) for c in possible_lengths]
    comb = possible_cuts[metrics.index(min(metrics))]
    paragraph = [' '.join(words[sum(comb[:i]):sum(comb[:i+1])]) for i in range(1, len(comb))]
    return '\n'.join(paragraph)


def view_box(
        coordinates: dict
):
    """
    Crop the SVG with a viewBox to the coordinates indicated.

    :param coordinates: (dict['x0': float, 'y0': float, 'x1': float, 'y1': float]) coordinates of the top left (x0, y0)
        and bottom right (x1, y1) corners of the viewBox.
    :return: (str) SVG instructions to apply the viewBox.
    """
    x, y = coordinates["x0"], coordinates["y0"]
    w, h = rounding(coordinates["x1"] - x, 3), rounding(coordinates["y1"] - y, 3)
    return f'width="{rounding(w * 10, 3)}" height="{rounding(h * 10, 3)}" viewBox="{x} {y} {w} {h}"'


def warnings_on_one_line(message, category, filename, lineno, file=None, line=None):
    """
    Makes Python's `warnings.warn()` not mention itself.
    """
    return '%s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)
