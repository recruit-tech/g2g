#/usr/bin/python3
# coding: utf-8

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
import math
from typing import List, Tuple, Optional, Dict
import parse
from blockdiag.command import main as blockdiag_main

# matplotlib colors
colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

def shape_string(string: str) -> str:
    """ shape string (remove space)

    Args:
        string: string you want to shaping

    Returns:
        shaped(space removed) string
    """
    string.replace(" ", "")
    return string

def get_dataframe(book_name:str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """get dataframe from excel file.

    Args:
        book_name: name of excel file.

    Returns:
        node dataframe, color dataframe.
    """
    EXL = pd.ExcelFile(book_name)
    df_color = EXL.parse("color")
    df_node = EXL.parse("node")
    return df_node, df_color

def is_color(string: str) -> bool:
    """ Return the string passed is whether or not intended to represent the color.

    "string indicate color" means
    RGB(%d, %d, %d), or
    matplotlib color
        false: it isn't color.
    """
    string = shape_string(string)
    return ((parse.parse("RGB({:d},{:d},{:d})", string) is not None) or (string in colors))


def get_code(string: str) -> str:
    """ RGB(%d,%d,%d) or matplotlib color(e.g. red, blue ...) -> RGB(%02X, %02x, %02X)(e.g. #AABBCC)

    from decimanl numbered RGB or matplotlib color to hex numbered RGB
    if you want to add rule, add convert method in this function

    Args:
        string: string data to convert to hex number

    Returns:
        RGB data written in hex number

    Raise:
        if string is not indicate color, raise ValueError
    """

    if not is_color(string):
        raise ValueError("color code must be matplotlib colors or RGB(%d, %d, %d)")
    # RGB(%d, %d, %d) style
    if "RGB" in string:
        a = parse.parse("RGB({:d},{:d},{:d})", string)
        return '#%02X%02X%02X' % (a[0], a[1], a[2])
    # matplotlib color style
    elif string in colors:
        return colors[string]

def is_selector(string: str, selector_method_dict) -> bool:
    """ Return the string passed is whether or not "selector".

    selector is a function that determines nodes to color.

    Args:
        string: String for determining whether it is a selector
        selector_method_dict: selector:method dict

    Returns:
        is string selector?
    """

    # RGB() is not selector(color)
    if is_color(string): return False
    func = parse.parse("{}({})", string)
    # string is func
    if(func is not None):
        name = func[0]
        args = func[1].split(",")
        print("string:", string)
        print("name:", name)
        print("args:", args)
        return name in selector_method_dict
    return False

def get_method_value(string: str) -> Optional[Tuple[str, List[float]]]:
    """ selector XXXXXX(value) => XXXXXX, [float(value)].

    separate function name and argument.

    Args:
        string: string data to separate.

    Returns:
        function name, argument value.
    """
    func = parse.parse("{}({})", string)
    name = func[0]
    args = func[1].split(",")
    return name, args


def get_selector_color_dicts(df_color: pd.DataFrame, selector_method_dict):
    """ make selector_color_dict from df_color(excel file).

    selector_color_dict means "Which range shows which color".
    TODO: %で割合にする仕様を追加する
    10 RGB(255,0,0) 20 TOP3 RGB(0,255,0) ...
    => [{selector: equation, color: colormap or color or [color] }]
    selector: MINMAX ... MIN <= x <= MAX 's color is "color"Args:
    selector: TOPx ... TOP x 's color is "color"    df_color: color data readed from excel file.
        selector_method_dict: (selector: method(function)) dict.

    Returns:
        selector_color_dict: Which range shows which color
    """

    # first, Interpret each line
    # [("color", colorcode) or ("selector", {"method":method, value:value}) or ("number", value)]
    selector_number_color_dict = []
    # get first column name
    column_name = df_color.columns[0]

    for i in range(df_color[column_name].size):
        row = df_color[column_name][i]
        row = str(row)
        # color
        if is_color(row):
            selector_number_color_dict.append(("color", get_code(row)))
        # selector
        elif is_selector(row, selector_method_dict):
            method, values = get_method_value(row)
            selector_number_color_dict.append(("selector", {"method": method, "values": values}))
        # number
        else:
            selector_number_color_dict.append(("number" , row))

    # make MINMAX method from Color sandwiched between numbers
    selector_color_dicts = [];
    for i in range(len(selector_number_color_dict)):
        if(selector_number_color_dict[i][0] == "color"):
            # default number is nan
            # prv: preview row
            prv = ""
            # nxt: next row
            nxt = ""
            # sel: selector
            sel = ""

            # if prev is selector, this color's selector is this
            if(1 <= i and selector_number_color_dict[i-1][0] == "selector"):
                sel = selector_number_color_dict[i-1][1]
            # elif prev is number this color's selector is MINMAX
            if(1 <= i and selector_number_color_dict[i-1][0] == "number"):
                prv = selector_number_color_dict[i-1][1]
            # if next is number this color's selecor is MINMAX
            if(i < len(selector_number_color_dict)-1 and selector_number_color_dict[i+1][0] == "number"):
                nxt = selector_number_color_dict[i+1][1]

            # if this row means selector, add as it is
            if(sel != ""): selector_color_dicts.append({"selector": sel, "color" : selector_number_color_dict[i][1]})
            # else it means MINMAX selector
            else: selector_color_dicts.append({"selector": {"method": "MINMAX", "values": [prv, nxt]}, "color" : selector_number_color_dict[i][1]})

    return selector_color_dicts

def get_name_color_dict(df_node: pd.DataFrame, column_name, selector_method_dict, selector_color_dicts):
    """ make correspondence dict of which name indicates which color.
et
    Args:
        df_node: node dataframe
        column_name:
        selector_method_dict: selector:method dict
        selector_color_dicts: [selector:color] dict

    Returns:
        correspondence dict of which name indicates which color.
    """
    name_color_dict = {}
    for dic in selector_color_dicts:
        method = dic["selector"]["method"]
        values = dic["selector"]["values"]
        color = dic["color"]
        if(method in selector_method_dict):
            selected_row = selector_method_dict[method](df_node, column_name, values)
            print(selected_row)

        if "名前" in df_node.columns:
            for n in selected_row["名前"]:
                name_color_dict[n] = color

    return name_color_dict

def to_diag(output_filename:str, edge_filename:str, df_node:pd.DataFrame, name_color_dict) -> None:
    """ make diag data from df_node, name_color_dict

    Args:
        output_filename: output filename
        edge_filename: edge filename(aaa -> bbb; bbb->ccc ...)
        df_node: node dataframe (from excel file)
        name_color_dict: dict data maked by get_name_color_dict
    """
    # make label for output blockdiag file
    df_node["label"] = df_node["名前"] + " \\n "
    for column_name in df_node:
        if(column_name == "名前" or column_name == "label"): continue
        df_node["label"] += str(column_name) + ": " + df_node[column_name].astype(str) + " \\n "

    # Cut off the last 4 characters (eliminate the last newline)
    df_node["label"] = df_node["label"].map(lambda x:x[:-4])

    # Variable for deleting the last}
    last_bracket_pos = 0
    i = 0
    output = []
    for line in open(edge_filename):
        output.append(line)
        if('}' in line):
            last_bracket_pos = i
        i += 1

    # remove last "}"
    output = output[:last_bracket_pos]

    output.append('\n')

    # get text_
    max_text_width_length = 0
    max_text_height_count = df_node.shape[1]
    for column in df_node:
        if(column == "label"): continue
        if(column == "名前"): cnt = df_node[column].astype(str).str.len()[1:].max()
        else: cnt = df_node[column].astype(str).str.len()[1:].max() + len(str(df_node[column][0])) # 横幅
        max_text_width_length = max(max_text_width_length, cnt)

    # set node size
    font_size = 7
    height = 40 + max_text_height_count*font_size # default heigth size is 40
    width = 128 + max_text_width_length*font_size # default width size is 128

    # node information
    for key, row in df_node.iterrows():
        output.append(row["名前"] + "[label=\"" + row["label"] + "\", color=\"" + name_color_dict[row["名前"]] +"\",height="+str(height)+",width="+str(width)+"];\n");

    # add last "}"
    output.append('}')

    f = open(output_filename, 'w')
    f.writelines(output)
    f.close()


# method names

def get_top(df_node, column_name, values):
    selected_row = df_node.copy();
    value = int(values[0])
    selected_row = df_node.copy()
    selected_row = selected_row.nlargest(value, column_name)
    return selected_row

def min_max(df_node, column_name, values):
    print(values)
    selected_row = df_node.copy();
    maxi = df_node[column_name].max()
    mini = df_node[column_name].min()
    left = -math.inf
    right = math.inf
    print(mini, maxi)
    if(values[0][-1:] is "p"):
        per = float(values[0][:-1]) / 100.0
        left = (maxi-mini) * per + mini
        print(left)
    elif(values[0] is not ""):
        left = float(values[0])
    if(values[1][-1:] is "p"):
        per = float(values[1][:-1]) / 100.0
        right = (maxi-mini) * per + mini
        print(right)
    elif(values[1] is not ""):
        right = float(values[1])

    selected_row = selected_row[left <= selected_row[column_name]]
    selected_row = selected_row[right > selected_row[column_name]]
    return selected_row

default_selector_method_dict = {
    "TOP": get_top,
    "MINMAX": min_max,
}

if __name__ == '__main__':
    # read data
    df_node, df_color = get_dataframe("sample/data.xlsx")
    # selector:color dict
    selector_color_dicts = get_selector_color_dicts(df_color, default_selector_method_dict)
    # row name:color dict
    name_color_dict = get_name_color_dict(df_node,df_color.columns[0],default_selector_method_dict, selector_color_dicts)
    # output file
    to_diag("sample/out.diag", "sample/map.diag", df_node, name_color_dict)
    blockdiag_main(["-Tpdf", "sample/out.diag"]) # output pdf
    blockdiag_main(["sample/out.diag"]) # output png
