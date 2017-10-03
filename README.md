# What's this

サービスのTOP画面からの遷移図をnode-edge な raphにうまく描画してくれるツールです

# requirements

```
 easy_install -U reportlab
```

# How To Use

(仕様が固まっていないので概要のみ)

1. .xlsxファイルを書く
2. node-edgeの情報を書く
2. pythonを起動する
3. blockdiagを起動する

## Excelファイルの書き方

各sheetに必要な情報を書きます

sheetはそれぞれ

* readme
* node
* color

の3つに分類されます

### readme sheet

excelシートの使いかたを書くスペースです
node や colorの具体的な書き方の例はこちらのシートを参照してください

### node sheet

各nodeの設定を書くスペースです
nodeとそれに付随する情報を書きます(アクション貢献度と訪問数など)

### color

色の設定を行います。
x-yの間はRGB(255, 255,255),
y-zの間はRGB(0,0,0)
のようなthreadsholdな指定と
redtoblue
などのグラデーションの設定ができるようになっています

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

# ToDo

* Exampleを追加する
