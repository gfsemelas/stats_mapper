from mapper.transform import make_thresholds, make_palette, build_svg


def draw_map(
        data: dict,
        task: str = 'values',
        source_map: list = None,
        smart: bool = False,
        palette_style: str = 'RdYlBu',
        invert_palette: bool = False,
        force_default_palette: str = 'Reds',
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
    Colors a map by country with the given data.
    
    :param data: (dict[*str: float]) data.
    :param task: (str) method for building the thresholds that determine the map coloring.
    :param source_map: (list[*str], default=None) base map to use. Any combination of "africa", "antarctica", "asia",
        "europe", "north_america", "oceania", "south_america" and "world", followed or not followed each one by "*" to
        include intercontinental territories.
    :param smart: (bool, default=True) whether to try to fix errors with slight changes in possible wrong parameters.
    :param palette_style: (str) palette name, or sequence of Hex and/or RGB colors separated by underscores.
    :param invert_palette: (bool, default=False) whether to use the palette colors with their order inverted.
    :param force_default_palette: (str, default='Reds') if "Reds", "Greens" or "Blues" return a safe default palette
        of the given color if the provided `palette_style` makes the function fail for not being in the dictionary of
        palettes, for not having enough colors or for not being a valid sequence of Hex and/or RGB colors.
    :param missing_color: (str, default='#e6e6e6') color for the missing countries.
    :param ocean_color: (str, default='255,255,255') color for the oceans, seas and lakes.
    :param add_legend: (int, default=1) if 0 do not add legend to the map, if 1 add automatic legend to the map, if 2
        add a highest-lowest legend to the map.
    :param aliases: (dict[*int: str], default=None) if `add_legend` evaluates to True, dictionary matching the keys in
        `intensities` with the provided descriptions to overwrite the automatic legend.
    :param language: (str, default='math') if `add_legend` evaluates to True, language to use for the automatic legend.
    :param decimals: (int, default=0) if `add_legend` is 1, number of decimals for the numbers in the automatic legend.
    :param colors_used_only: (bool, default=True) if `add_legend` is 1, whether to drop from the automatic legend the
        color bins that do not represent any country.
    :param text_box: (str, default=None) text to display on the map if provided.
    :return: (str) SVG source code.
    """
    # Calculate thresholds and intensities
    thresholds, intensities = make_thresholds(
        task=task,
        data=data,
        smart_clean=smart
    )

    # Construct palette
    palette = make_palette(
        palette_style=palette_style,
        n_colors=len(thresholds) + 1,
        smart=smart,
        invert_palette=invert_palette,
        force_default_palette=force_default_palette
    )

    # Build SVG
    if task == 'values' and aliases is None:
        aliases = {i: v for i, v in enumerate(sorted(list(set(data.values()))))}
    svg = build_svg(
        thresholds=thresholds,
        intensities=intensities,
        palette=palette,
        source_map=source_map,
        missing_color=missing_color,
        ocean_color=ocean_color,
        add_legend=add_legend,
        aliases=aliases,
        language=language,
        decimals=decimals,
        colors_used_only=colors_used_only,
        text_box=text_box
    )

    return svg
