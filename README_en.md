# g2g

サービスのTOP画面からの遷移図をnode-edge な graphにうまく描画してくれるツールです
![](./sample/out.png)

# Quick Start

```
git clone https://github.com/recruit-tech/g2g
cd g2g
python g2g.py sample/data.xlsx sample/map.diag out # => make out.png, out.pdf, out.diag
```

`git`コマンドに失敗する方は，`git`のインストールを試みてください．
あるいは，githubのページからDownload Zipを選択してzipを解凍してください．

# requirements

python: 3.6.3

必要なパッケージは，
```
pip install -r requirements.txt
```
でインストールすることができます．もし，実行できない場合はバージョン互換性に問題がある可能性があります．その場合は，
```
pip install -c constraints.txt -r requirements.txt
```
を試してみてください．
# How To Use

1. .xlsxファイルに各ページ(ノード)の情報を書く
2. .diagファイルにページ間の遷移情報を書く
2. `python g2g.py xlsxファイル diagファイル 出力ファイル名` と書く
3. `出力ファイル名.diag`ファイルと, `出力ファイル名.pdf`ファイルが生成される．

## Excelファイルの書き方

各sheetに必要な情報を書きます

sheetはそれぞれ

* readme
* node
* color

の3つに分類されます

### readme sheet

* excelシートの使いかたやメモなどを書くスペースです
* プログラム実行時には無視されます．
* node や colorの具体的な書き方の例はreadme sheetを参照してください

### node sheet

* 各nodeの設定を書くスペースです
* nodeとそれに付随する情報を書きます(訪問数や離脱率など)

### color

色の設定を行います。
詳しくは，sampleのreadme sheetを確認してください．

## node-edge情報の記述方法

blockdiagの書き方です。
こちらを参照してください.(http://blockdiag.com/ja/blockdiag/examples.html#simple-diagram)

かんたんな例
```
blockdiag {
   A -> B -> C -> D;
   A -> E -> F -> G;
}
```
# sampleの実行方法

```
python g2g.py sample/data.xlsx sample/map.diag out
```

# 独自の選択関数の追加方法

excelのcolorで必要な関数を独自に定義することができます．

`method.py`に関数を追加します．

関数を追加するために，3つの手順が必要です

1. 3つの引数を持つ関数を定義する
2. 関数を実装する
3. `selector_method_dict`に名前を追加する

## 3つの引数を持つ関数を定義する

関数名は自由で，3つの引数を持つ関数を定義します．

```python
def method_name(df_node, column_name, values)
```
* `df_node`: excelファイルのnodeに対応するnodeの情報が渡されます．(pandasのDataframe型)
* `column_name`: excelファイルの`color`で選択されている行の情報が渡されます(str型)
* `values`: excelファイルで指定された値が渡されます(strのarray)

## 関数を実装する

関数の返り値は，`df_node`から選択した行だけを残すようにフィルタした結果を返します(pandasのDataframe型)

以下の例は`TOP`のものです．`TOP(x)`では，ひとつの引数が渡され上位`x`個を選択することができる関数です．
```python
def get_top(df_node, column_name, values): # 3つの引数を持つ関数を定義する
    selected_row = df_node.copy();
    value = int(values[0]) # valueをint型に変更する
    selected_row = df_node.copy() # 行を選択するためのdataframeを用意する
    selected_row = selected_row.nlargest(value, column_name) # column_name列に関する上位value個を取り出す
    return selected_row # 選択した結果を返す
```

## `selector_method_dict`に名前を追加する

`methods.py`の一番下に以下のようなdictionaryがあります．
これに名前を登録することで，excelファイルから呼び出すことができます．

* key: excelファイルから呼び出す関数名
* value: keyで指定した関数名から呼び出す関数

keyはexcelの関数にならってすべて大文字の命名をしています．

```python
selector_method_dict = {
    "ALL": all_row,
    "TOP": get_top,
    "BOTTOM": get_bottom,
    "MINMAX": min_max,
}
```