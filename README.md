```
     _        _
 ___| |_ __ _| |_ ___     _ __ ___   __ _ _ __  _ __   ___ _ __
/ __| __/ _` | __/ __|   | '_ ` _ \ / _` | '_ \| '_ \ / _ \ '__|
\__ \ || (_| | |_\__ \   | | | | | | (_| | |_) | |_) |  __/ |
|___/\__\__,_|\__|___/___|_| |_| |_|\__,_| .__/| .__/ \___|_|
                    |_____|              |_|   |_|
```
Get geographic maps with countries colored from quantitative or qualitative data, using the 2-digit ISO codes.

**— IMPORTANT NOTE:** there is a *requirements.txt* file which you can use to install the necessary dependencies. Feel free to use `pip install -r requirements.txt` in non-Windows systems. However, if you are working with Windows this will not work due to [this issue](https://cairocffi.readthedocs.io/en/stable/overview.html#installing-cairo-on-windows) related with `cairosvg` library, in which case you will need to fix the issue for your system yourself, or use an Anaconda environment and install the dependencies via `conda install -c conda-forge --file requirements.txt`.

**— METHOD:** execute `draw_gui.py` to start the GUI where you can specify the options to generate your map, or execute `draw.py` to specify those options as arguments in the command line.

- ***draw_gui.py*** inputs:
  - **Data_file**: path to the file with the data.
  - **CSV separator**: CSV-separator if `Data file` is a CSV file.
  - **Sheet name**: sheet where the data are if `Data file` is a spreadsheet.
  - **Countries 2-digit ISO codes column**: name of the column where the countries are if `Data file` is a spreadsheet.
  - **Data_col**: name of the column where the numeric data or the labels are if `Data file` is a spreadsheet.
  - **Task**: how to segment the data to color the countries in bins. Options are:
    - `"values"`: a color per numeric value.
    - `"b:{n}"`, where `{n}` is a positive integer: divide all numeric data in this number of equally distributed bins and associate a color to each bin.
    - `"t:{s}"`, where `{s}` is a comma-separated string of numbers: numeric thresholds in which to divide the bins.
    - `"sign"`, `"mean"` / `"average"`, `"median"` or `"std"`: two bins containing all data over and under the selected metric.
    - EXAMPLES: `"b:4"`, `"t:4,8,20"`, `"t:1m,1,1K,1M"`, `"average"`.
  - **Source map**: comma-separated string of continents that should appear in the map. To ensure that a continent includes countries with part of their territory in other continents, add an asterisk (`"*"`) at the end of its name. Possible continents are: `"Africa"`, `"Antarctica"`, `"Asia"`, `"Europe"`, `"North America"`, `"Oceania"` and `"South America"`. For the whole world to appear, indicate `"World"`. (Names are not case-sensitive).
    - EXAMPLES: `"Europe*"`, `"africa"`, `"North America`, `South America"`.
  - **Smart**: if `"Yes"`, the program will try to fix all possible errors that arise due to wrong inputs with default values. If `"No"`, the program will rise the first error it encounters.
  - **Add legend**: `0` to hide the legend, `1` to show it, `2` to show only maximum and minimum values.
  - **Palette style**: palette name (as of https://colorbrewer2.org/) or sequence of Hex and/or 3-tuple RGB colors, separated by underscores. If the sequence of colors is chosen, it should include as many colors as bins in which the data have been segmented with parameter `Task`.
    - EXAMPLES: `"PuBuGn"`, `"Spectral"`, `"200,50,50_150,100,100"`, `"#fc8d59_98,34,143_#ef8a62"`
  - **Invert palette**: palettes are an ordered sequence of colors. It could be possible that the red is associated with the lowest datum and the blue with the highest in the map, and you want that upside down. This parameter allows you to do this by setting it to `"Yes"` or `"No"`.
  - **Force default palette**: if the `Palette style` input contains errors or the requested palette does not have enough colors, `Smart` parameter will try to fix this. If `Smart` is not activated, or it is but cannot fix the problem, this parameter allows you to use a safe palette without crashing the program if its value is `"Reds"`, `"Greens"` or `"Blues"`, using then the corresponding palette.
  - **Missing**: Hex or 3-tuple RGB color which should fill the countries in the map that do not appear in the data.
  - **Ocean**: Hex or 3-tuple RGB color which should fill the ocean, seas and lakes in the map.
  - **Legend aliases**: if your data is qualitative and not quantitative, you will have used integer labels for countries in the data file and given `"values"` in parameter `Task`. If you wish to use your qualitative identifiers and not the numeric labels, indicate `"Yes"` here and a file-selection window will appear, where you should select a JSON file that acts as a Python dictionary mapping the labels (keys) with the qualitative identifiers (values).
  - **Language**: if `Legend aliases` is `"No"`, the legend will show numeric intervals in the provided language. Choose here that language among `"en"` (English), `"es"` (Spanish), `"de"` (German), `"math"` (mathematical style) and `"nerd"` (algebraic style).
  - **Decimals**: 0 or positive integer for the number of decimals that the numbers of the legend should have if no `Legend aliases` was provided.
  - **Colors used only**: when computing bins and thresholds, it is possible that some bins do not represent any country. Indicate `"Yes"` to omit these bins from the legend.
  - **Text box**: text to include on the map, like a title or a note. Leave blank if you do not wish any.
  - **Bitmap**: `"Yes"` to save the map as PNG, `"No"` to save the map as SVG.
  - **DPI**: dots per inch of the PNG if `Bitmap` is `"Yes"`.
  - **Width**: width of the PNG if `Bitmap` is `"Yes"`. Leave `"auto"` for automatic width.
  - **Out map**: path to the generated map image.

- ***draw.py*** command line arguments:
  - `data_file`: (`str`) path to the file with the data.
  - `-z`, `--out_map`: (`str`, default=`None`) path to the generated map image.
  - `-c`, `--separator`: (`str`, default=`","`) separator if `file` is a CSV file.
  - `-r`, `--sheet`: (`str`, default=`"Sheet1"`) sheet where the data are if `file` is a spreadsheet.
  - `-u`, `--countries_col`: (`str`, default=`"COUNTRY"`) name of the column where the countries are if `file` is a spreadsheet.
  - `-n`, `--data_col`: (`str`, default=`"DATA"`) name of the column where the numeric data or the labels are if `file` is a spreadsheet.
  - `-t`, `--task`: (`str`, default=`"values"`) how to segment the data to color the countries in bins.
  - `-m`, `--source_map`: (`*str`, default=`None`) map to draw (any combination of `"africa"`, `"antarctica"`, `"asia"`, `"europe"`, `"north_america"`, `"oceania"`, `"south_america"` and `"world"`, followed or not followed each one by `"*"` to include intercontinental territories).
  - `-s`, `--smart`: (`bool`, default=`True`) whether to try to fix errors with slight changes in possible wrong parameters.
  - `-p`, `--palette_style`: (`str`, default=`"RdYlBu"`) palette name or sequence of Hex and/or 3-tuple RGB colors, separated by underscores.
  - `-i`, `--invert_palette`: (`bool`, default=`False`) whether to use the palette colors with their order inverted.
  - `-f`, `--force_default_palette`: (`str`, default=`"Reds"`) if `"Reds"`, `"Greens"` or `"Blues"` safe default palette to use if the palette assignation fails.
  - `-g`, `--missing`: (`str`, default=`"#e6e6e6"`) color for the countries that are missing in the data.
  - `-o`, `--ocean`: (`str`, default=`"255,255,255"`) color for the oceans, seas and lakes in the map.
  - `-l`, `--add_legend`: (`int`, default=`1`) whether to show the legend in the map. If `0`, do not. If `1`, do. If `2`, only maximum and minimum values are displayed.
  - `-k`, `--legend_aliases`: (`str`, default=`None`) path to a JSON file with the mapping between the labels of each country and their description in the legend.
  - `-a`, `--language`: (`str`, default=`"math"`) language of the legend. Available ones are `"en"`, `"es"`, `"de"`, `"math"` and `"nerd"`.
  - `-e`, `--decimals`: (`int`, default=`0`) number of decimals to show in the numbers that appear in the legend.
  - `-y`, `--colors_used_only`: (`bool`, default=`True`) whether to delete from the legend the colors and intervals with no countries in them.
  - `-b`, `--bitmap`: (`bool`, default=`True`) whether to save the map as a PNG file, or leave it as an SVG file.
  - `-d`, `--dpi`: (`int`, default=`96`) DPIs for the image if it is saved in PNG format.
  - `-w`, `--width`: (`float`, default=`None`) width in pixels of the image if it is saved in PNG format. If `None`, automatic width is set.
  - `-x`, `--text_box`: (`str`, default=`None`) text to add to the image if it is saved in PNG format.
