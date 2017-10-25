import math

def get_top(df_node, column_name, values):
    selected_row = df_node.copy();
    value = int(values[0])
    selected_row = df_node.copy()
    selected_row = selected_row.nlargest(value, column_name)
    return selected_row

def get_bottom(df_node, column_name, values):
    selected_row = df_node.copy();
    value = int(values[0])
    selected_row = df_node.copy()
    selected_row = selected_row.nsmallest(value, column_name)
    return selected_row

def all_row(df_node, column_name, values):
    return df_node

def min_max(df_node, column_name, values):
    values[0].replace(" ", "")
    values[1].replace(" ", "")
    selected_row = df_node.copy();
    left = -math.inf
    right = math.inf

    mini = df_node[column_name].min()
    maxi = df_node[column_name].max()

    try:
        if values[0][-3:] == "per":
            values[0] = (maxi - mini)*float(values[0][:-3])/100.0 + mini
        if values[0] != "": left = float(values[0])
    except ValueError as e:
        raise ValueError("MINMAX exception \"" + values[0] + "\" is not float value. please input number or number+\"per\"")

    try:
        if values[1][-3:] == "per":
            values[1] = (maxi - mini)*float(values[1][:-3])/100.0 + mini
        if values[1] != "": right = float(values[1])
    except ValueError as e:
        raise ValueError("MINMAX exception \"" + values[1] + "\" is not float value. please input number or number+\"per\"")

    if(left != ""): selected_row = selected_row[left <= selected_row[column_name]]
    if(right != ""): selected_row = selected_row[right > selected_row[column_name]]
    return selected_row

selector_method_dict = {
    "ALL": all_row,
    "TOP": get_top,
    "BOTTOM": get_bottom,
    "MINMAX": min_max,
}
