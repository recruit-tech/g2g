#/usr/bin/python3
# coding: utf-8

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from typing import List, Tuple, Optional, Dict
import parse
from blockdiag.command import main as blockdiag_main
import sys
import methods
import math
import platform
import os

# matplotlib colors
colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)
colors["danger"] = "#FF0C0C"
colors["safe"] = "#041A99"
colors["appeal"] = "#00FF6E"
colors["superappeal"] = "#FFFF00"
color_maps = sorted(m for m in plt.cm.datad if not m.endswith("_r"))
color_maps.append("default")

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

def get_color_code(string: str) -> Optional[str]:
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

    string = shape_string(string)
    parse_string = parse.parse("RGB({:d},{:d},{:d})", string);
    # RGB(%d, %d, %d) style
    if parse_string is not None:
        a = parse.parse("RGB({:d},{:d},{:d})", string)
        return '#%02X%02X%02X' % (a[0], a[1], a[2])
    # matplotlib color style
    elif string in colors:
        return colors[string]
    else:
        return None

def get_method_value(string: str) -> Optional[Tuple[str, List[float]]]:
    """ selector XXXXXX(value) => XXXXXX, [float(value)].

    separate function name and argument.

    Args:
        string: string data to separate.

    Returns:
        function name, argument value.
    """
    string = shape_string(string)
    if get_color_code(string) is not None:
        return None, None
    func = parse.parse("{}({})", string)
    if func is None:
        func_empty_arg = parse.parse("{}()", string)
        if func_empty_arg is None:
            return None, None
        elif func_empty_arg[0] in methods.selector_method_dict:
            return func_empty_arg[0], None
    name = func[0]
    args = func[1].split(",")
    if name in methods.selector_method_dict:
        return name, args
    return None, None

def get_color_map_value(string: str) -> Optional[Tuple[str, float, float]]:
    """ color_map(min, max) => colormap, min, max

    separate function name and argument

    Args:
        string: string data to separate

    Returns:
        function name, min, max
    """
    string = shape_string(string)
    if string in color_maps:
        return string, None, None

    func = parse.parse("{}({},{})", string)
    if func is None:
        return None, None, None
    if func[0] not in color_maps:
        return None, None, None
    return func[0], float(func[1]), float(func[2])

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
        code = get_color_code(row)
        method, values = get_method_value(row)
        color_map, min_value, max_value = get_color_map_value(row)
        # color
        if code is not None:
            selector_number_color_dict.append(("color", code))
        elif color_map is not None:
            selector_number_color_dict.append(("color_map", {"name": color_map, "min": min_value, "max": max_value}))
        # selector
        elif method is not None:
            selector_number_color_dict.append(("selector", {"method": method, "values": values}))
        # number
        else:
            try:
                float(row)
                selector_number_color_dict.append(("number" , row))
            except:
                try:
                    float(row[:-3])
                    selector_number_color_dict.append(("number" , row))
                except:
                    raise ValueError("\"" + row + "\" is not defined")

    print(selector_number_color_dict)
    # make MINMAX method from Color sandwiched between numbers
    selector_color_dicts = []
    for i in range(len(selector_number_color_dict)):
        if(selector_number_color_dict[i][0] == "color" or selector_number_color_dict[i][0] == "color_map"):
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
            if(sel != ""): selector_color_dicts.append({"selector": sel, selector_number_color_dict[i][0] : selector_number_color_dict[i][1]})
            # else it means MINMAX selector
            else: selector_color_dicts.append({"selector": {"method": "MINMAX", "values": [prv, nxt]}, selector_number_color_dict[i][0] : selector_number_color_dict[i][1]})

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
        if(method in selector_method_dict):
            try:
                selected_row = selector_method_dict[method](df_node, column_name, values)
            except BaseException as e:
                raise BaseException(e)

        if "color_map" in dic:
            color_map = dic["color_map"]["name"]
            if(color_map == "default"):
                color_map = "coolwarm"
            cmap = plt.cm.get_cmap(color_map)
            mi = (selected_row[column_name].min() if (dic["color_map"]["min"] is None) else dic["color_map"]["min"])
            ma = (selected_row[column_name].max() if (dic["color_map"]["max"] is None) else dic["color_map"]["max"])
            selected_row["ratio"] = (selected_row[column_name] - mi)/(ma-mi)
            for i, v in selected_row.iterrows():
                color_value = cmap(v["ratio"])
                color_code = '#%02X%02X%02X' % (int(color_value[3]*color_value[0]*255), int(color_value[3]*color_value[1]*255), int(color_value[3]*color_value[2]*255))
                name_color_dict[v["名前"]] = color_code;

        elif "color" in dic:
            color = dic["color"]
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

    output.insert(1, "default_fontsize=16;\n")

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
    font_size = 10
    height = 40 + max_text_height_count*font_size # default heigth size is 40
    width = 128 + max_text_width_length*font_size # default width size is 128

    # node information
    for key, row in df_node.iterrows():
        try:
            node_color = name_color_dict[row["名前"]]
        except KeyError as e:
            print("Warning: " + row["名前"] + " is not colored. this node will be white")
            continue
        text_color = "#000000" if int(node_color[1:3], 16)*0.299 + int(node_color[3:5], 16)*0.587 + int(node_color[5:7], 16)*0.114 > 127 else "#FFFFFF"
        output.append(row["名前"] + "[label=\"" + row["label"] + "\", color=\"" + node_color + "\", textcolor=\"" + text_color + "\",height="+str(height)+",width="+str(width)+"];\n");

    # add last "}"
    output.append('}')

    f = open(output_filename, 'w')
    f.writelines(output)
    f.close()

def print_usage():
    print('Usage: python {} excel_file diag_file out [fontmaprc]'.format(__file__))
    print("Arguments:")
    print("  excel_file: excel file contain node and color data")
    print("  diag_file: file in which page transitions are written in graphs")
    print("  out: filename for output. this app output 2files : <out>.pdf & <out>.diag ")
    print("  fontmaprc: font setting file");

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print_usage()
        exit(1)
    # read data
    df_node, df_color = get_dataframe(sys.argv[1])
    # selector:color dict
    selector_color_dicts = get_selector_color_dicts(df_color, methods.selector_method_dict)
    print(selector_color_dicts)
    # row name:color dict
    name_color_dict = get_name_color_dict(df_node,df_color.columns[0],methods.selector_method_dict, selector_color_dicts)
    # output file
    to_diag(sys.argv[3] + ".diag", sys.argv[2], df_node, name_color_dict)
    if len(sys.argv) < 5:
        os.system("blockdiag  -Tpdf " + sys.argv[3] + ".diag")
        os.system("blockdiag  -a  " + sys.argv[3] + ".diag")
    else:
        print("blockdiag --fontmap="+sys.argv[4]+" -Tpdf " + sys.argv[3] + ".diag")
        os.system("blockdiag --fontmap="+sys.argv[4]+" -Tpdf " + sys.argv[3] + ".diag")
        os.system("blockdiag  -a --fontmap="+sys.argv[4] + " " + sys.argv[3] + ".diag")
