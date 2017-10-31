
# g2g

g2g is a graph(graph theory) drawing tool for service transition diagram.

![](./sample/out.png)

# Getting Started

## Prerequisites

```
git
python 3.6.3
```

## Install & Running sample
```
git clone https://github.com/recruit-tech/g2g
cd g2g
pip install -r requirements.txt
python g2g.py sample/data.xlsx sample/map.diag out # => make out.png, out.pdf, out.diag
```

# How To Use

1. write node datas to .xlsx file.
2. write page transition data to .diag file
3. `python g2g.py xlsx_file diag_file output_filename` と書く
4. generate `output_filename.diag` & `output_filename.pdf`.

## Excelファイルの書き方

write datas to each sheets.

excel file contains the following three sheets.

* readme sheet
* node sheet 
* color sheet

### readme sheet

* readme sheet is ignored at run time.
* please use it for a memo.
* this sheet contain "how to write excel sheets (now japanese only...)".

### node sheet

* this sheet contain the data of nodes.

### color

* this sheet contain the color data of nodes.
* in detail, please confirm "readme sheet"

## how to write node-edge datas

* write `.diag` file in blockdiag format (http://blockdiag.com/ja/blockdiag/examples.html#simple-diagram)

### example
```
blockdiag {
   A -> B -> C -> D;
   A -> E -> F -> G;
}
```

# How To run

```
python g2g.py excel_file diag_file output_filename(without filename extension)
```

```
python g2g.py sample/data.xlsx sample/map.diag out
```

# For add selection function.

This app can be added selection functions for "color sheet" yourself.

To add functions, please do the following three steps.

1. open `method.py` by editor.
2. define a function with three arguments.
3. implement the function
4. add function name and function to `selector_method_dict`.

## define a function with three arguments.

define a function with three arguments.
function name is free to decide.

```python
def method_name(df_node, column_name, values)
```
* `df_node`: node data coresspond to "excel node sheet" (pandas Dataframe)
* `column_name`: column name selected by "excel color sheet" (str type)
* `values`: values specified as an argument with excel ([str] type)

## implement the function

the return value of the functions is the result of filtering to leave only the line selected from `df_node` (pandas Dataframe)

the following example is `TOP`
`TOP(X)` is a function that allows one argument to be passed and upper `x` will be selected.
```python
def get_top(df_node, column_name, values): # define a function with three arguments
    selected_row = df_node.copy();
    value = int(values[0]) # cast values to int
    selected_row = df_node.copy() # prepare a dataframe to select lines.
    selected_row = selected_row.nlargest(value, column_name) # filter upper top `value`
    return selected_row # return filtered dataframe
```

## add function name and function to `selector_method_dict`.

the following dictionary type variable at the bottom of "methods.py".
By registering a name on this, you can call it from an excel file.

* key: function name to call from excel file.
* value: function.

```python
selector_method_dict = {
    "ALL": all_row,
    "TOP": get_top,
    "BOTTOM": get_bottom,
    "MINMAX": min_max,
}
```
