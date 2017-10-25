# What's this

サービスのTOP画面からの遷移図をnode-edge な raphにうまく描画してくれるツールです

# requirements

```
 pip install reportlab
 pip install parse
 pip install blockdiag
```

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