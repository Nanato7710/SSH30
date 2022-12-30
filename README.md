# SSH30

## 目次

- [目標](#目標)
  - [エコーチェンバー](#エコーチェンバー)
- [方法](#方法)
  1. [クエリテーマの入力](#1-クエリテーマの入力)
  2. [レスポンステキストの収集](#2-レスポンステキストの収集)
  3. [レスポンステキストの分類](#3-レスポンステキストの分類)
  4. [分類後のレスポンステキストの出力](#4-分類後のレスポンステキストを出力)
- [前提知識](#前提知識)
  - [ベクトル](#ベクトル)
  - [埋め込み表現](#埋め込み表現)
  - [コサイン類似度](#コサイン類似度)

## 目標

最近、エコーチェンバーというものを知りました。この状態では自分にとって有利な情報のみ集まりやすくなってしまい、自分以外の意見などを攻撃しやすくなってしまいます。\
これを改善または解決することが目標です。

<details>

<summary>エコーチェンバーとは</summary>

### エコーチェンバー

> SNS では、自分と似た価値観や考え方をもつユーザをフォローしがちで、結果的に、同じようなニュースや情報ばかりが流通する閉じた情報環境ができてしまう。\
> このような情報環境を，「エコーチェンバー（Echo Chamber）」という。\
> 出典 : [ウェブの功罪](https://www.jstage.jst.go.jp/article/jkg/70/6/70_309/_article/-char/ja/)

</details>

[目次へ戻る:back:](#目次)

## 方法

エコーチェンバーの中に真逆または関係のない情報を入れたらよいのではないかと考えました。
よって、今回は次の手順で実装を行いました。

1. [ユーザーの意見や主張（クエリテーマ）を入力](#1-クエリテーマの入力)
2. [データベース上から、クエリテーマと関係のある文章（レスポンステキスト）を収集](#2-レスポンステキストの収集)
3. [レスポンステキストを内容や意見ごとに分類](#3-レスポンステキストの分類)
4. [分類したレスポンステキストを出力](#4-分類後のレスポンステキストを出力)

### 1. クエリテーマの入力

今回はクエリテーマにある程度の制限をかけました。それは、感覚的ですが日常的によく用いられている単語のみで構成されているということです。\
下記の表のような感じです。

:o:/:x:|例文
:--:|:--
:o:|俺は猫派で、家では10匹の猫様に仕えている。
:o:|犬は私の良き友人です。猫なんかとは違って、きちんと約束を守るからです。
:x:|たけのこの里こそが至高。きのこの山派は山に帰れ。
:x:|炊き込みご飯には茸よりも筍派だ。

なぜなら、今回はSentence BERT（SBERT）を使用して文章の埋め込み表現を取得するのですが、モデルの学習で使用したコーパス内において使用頻度が少ない単語だと次のような問題が生じると考えられるからです。SBERTに文章を入力する前にトークン化という、文章を単語のようなトークンというものに区切る処理を行います。その際に、非推奨 :x: な文章を入力すると次のようになってしまいます。

入力|トークン化後
---|---
たけのこの里こそが至高。きのこの山派は山に帰れ。|['[CLS]', 'たけ', 'の', 'この', '里', 'こそ', 'が', '至', '##高', '。', 'きの', '##こ', 'の', '山', '派', 'は', '山', 'に', '帰', '##れ', '。', '[SEP]']
炊き込みご飯には茸よりも筍派だ。|['[CLS]', '炊', '##き', '##込み', 'ご飯', 'に', 'は', '[UNK]', 'より', 'も', '[UNK]', '派', 'だ', '。', '[SEP]']

`[CLS]`と`[SEP]`は文章の始めと終わり、`[UNK]`は未知語、`##`は前のトークンと接続されるということを示しています。\
上の表からわかるように、「たけのこの里」が`'この'`で区切れていたり、筍や茸が未知語として扱われてしまっています。\
以上のような理由からクエリテーマは日常的によく用いられている単語のみで構成されているという制限を設けました。

### 2. レスポンステキストの収集

レスポンステキストを集める方法としては、データベース上の文章とクエリテーマをSBERTを用いて各文章の埋め込み表現を取得し、コサイン類似度を測り、上位tok_k個集めてくる方法を採用しました。top_kはユーザーが任意で設定します。\
この方法を採用した理由は、埋め込み表現とコサイン類似度を用いて文章の類似度を測ることが一般的だったこと、表示する量を設定しやすくしたことの2つです。\

#### 問題点1

この方法の問題点は、top_k個の文章とクエリテーマの類似度が高すぎるとそれはエコーチェンバーとは変わりないことです。今回は、top_kを100以上にすることで対応しました。しかし、この方法はデータベースに依存してしまうのでコサイン類似度を使用した何らかの方法に切り替えたいと考えています。

### 3. レスポンステキストの分類

分類ではレスポンステキスト同士でコサイン類似度を測り、ある値（閾値）以上なら同じグループ、閾値未満なら別のグループというように分類する方法を採用しました。\
採用した理由は、レスポンステキストの収集方法を採用した時と同じ理由です。

### 4. 分類後のレスポンステキストを出力

これはそのままです。

[目次へ戻る:back:](#目次)

## 前提知識

この一覧の項目のうち知らないものがあれば、調べてくるか、詳細を見てください。知っていれば飛ばしてもらってかまいません。ここ見ることよりも、調べてくるほうがオススメです。なぜなら、ここから先は、私のマークダウンや文章、Mathjaxの練習として書いておりまた、先人のわかりやすい解説がネット上には多いからです。

<div id="prerequisite-knowledge">

- [ベクトル](#ベクトル)
- [埋め込み表現](#埋め込み表現)
- [コサイン類似度](#コサイン類似度)

</div>

### ベクトル

厳密には線形空間に属する元ならばベクトルと言えますがここではベクトルとは $n$ 個の実数 $\mathbb{R}$ が並んだ以下のようなものです。記号では $\mathbb{R}^n$ と書きます。
縦に並んでいるときと横に並んでいるときで区別する時はそれぞれ $\mathbb{R}^{n\times1}$ 、 $\mathbb{R}^{1\times{n}}$ と書きます。

$$
\begin{pmatrix}
  x_1 \\
  x_2 \\
  \vdots\\
  x_n
\end{pmatrix}
\in \mathbb{R}^{n}  \text{ and }  \mathbb{R}^{n \times 1}
$$

$$
\begin{pmatrix}
  x_1,x_2,\dotsb ,x_n
\end{pmatrix}
\in \mathbb{R}^n \text{ and } \mathbb{R}^{1 \times n}
$$

$$
\boldsymbol{a}
$$

これらには加法、減法が定められています。

$$
\text{let }\boldsymbol{a,b}\in\mathbb{R}^n\\
$$

```math
\begin{pmatrix}
  a_1 \\
  a_2 \\
  \vdots \\
  a_n 
\end{pmatrix}
+
\begin{pmatrix}
  b_1 \\
  b_2 \\
  \vdots \\
  b_n
\end{pmatrix}
=
\begin{pmatrix}
  a_1+b_1 \\
  a_2+b_2 \\
  \vdots \\
  a_n+b_n
\end{pmatrix}
```

```math
\begin{pmatrix}
  a_1 \\
  a_2 \\
  \vdots \\
  a_n \\
\end{pmatrix}
-
\begin{pmatrix}
  b_1 \\
  b_2 \\
  \vdots \\
  b_n \\
\end{pmatrix}
=
\begin{pmatrix}
  a_1-b_1 \\
  a_2-b_2 \\
  \vdots \\
  a_n-b_n \\
\end{pmatrix}
```

実数倍も定められています。

$$
\text{let }c \in \mathbb{R},\boldsymbol{a} \in \mathbb{R}^n\\
$$

```math
c
\begin{pmatrix}
  a_1 \\
  a_2 \\
  \vdots \\
  a_n \\
\end{pmatrix}
=
\begin{pmatrix}
  ca_1 \\
  ca_2 \\
  \vdots \\
  ca_n \\
\end{pmatrix}
```

そして、ベクトルの特徴的な操作として内積というものがあります。
それは以下のように2つのベクトルの各成分をかけて、その和をとったものです。

$$
\text{let }\boldsymbol{a,b} \in \mathbb{R}^n
$$

$$
\begin{align}
  \boldsymbol{a} \cdot \boldsymbol{b} &= \sum^{n}_{k=i}{a_kb_k} \\
  &= a_1b_1+a_2b_2+\cdots+a_nb_n
\end{align}
$$

一般的にベクトルの長さのことをノルム（厳密には $L^2$ ノルム）といい $n$ 次元ベクトル $\boldsymbol{a}$ のノルムを $||\boldsymbol{a}||$ と書きます。

$$
\text{let }\boldsymbol{a}\in\mathbb{R}^n
$$

$$
\begin{align}
  \|\boldsymbol{a}\| &= \sqrt{\sum^{n}_{k=1}{a_k^2}} \\
  &= \sqrt{a_1^2+a_2^2+\cdots+a_n^2}
\end{align}
$$

2つのベクトルのノルムがどちらも0でない時、内積の別の形の定義として2つのベクトルのとなす角 $\theta$ 、三角関数の $\cos$ そしてベクトルのノルムを用いたものがあります。

$$
\text{let }\boldsymbol{a,b}\in\mathbb{R}^n
$$

$$
\boldsymbol{a} \cdot \boldsymbol{b} = \|\boldsymbol{a}\|\|\boldsymbol{b}\|\cos \theta
$$

2つのベクトルのなす角 $\theta$ について、2次元や3次元の場合は直感的に理解できると思いますが、4、5、6… $n$ 次元のような3次元より大きくなった場合はどうするのでしょうか。\
この場合は、コーシーシュワルツの不等式と、 $-1 \leq \cos x \leq 1$ であることから次の等式を満たす実数 $\theta$ が存在することが示されます。これを2つの $n$ 次元ベクトルがなす角とします。\
コーシーシュワルツの不等式の証明については各自でご確認願います。個人的に、二次関数の判別式についての知識があればわかるであろう、学びTimesさんの高校数学の美しい物語で示されている[こちら](https://manabitimes.jp/math/573)の証明がオススメです。

<div id='cosine-similarity'>

$$
\text{let }  \boldsymbol{a,b} \in \mathbb{R}^n,\|\boldsymbol{a}\|\neq 0,\|\boldsymbol{b}\|\neq 0
$$

$$
\begin{align}
  &(\boldsymbol{a} \cdot \boldsymbol{b})^2 \leq \|\boldsymbol{a}\|^2\|\boldsymbol{b}\|^2\\
  \Leftrightarrow &\frac{(\boldsymbol{a} \cdot \boldsymbol{b})^2}{\|\boldsymbol{a}\|^2 \|\boldsymbol{a}\|^2} \leq 1\\
  \Leftrightarrow &-1 \leq \frac{\boldsymbol{a} \cdot \boldsymbol{b}}{\|\boldsymbol{a}\| \|\boldsymbol{a}\|} \leq 1\\
  \therefore & \text{ } \exists \theta\in\mathbb{R}\colon \cos \theta = \frac{\boldsymbol{a} \cdot \boldsymbol{b}}{\|\boldsymbol{a}\| \|\boldsymbol{a}\|}\\
  \Leftrightarrow \text{ } & \boldsymbol{a} \cdot \boldsymbol{b} = \|\boldsymbol{a}\| \|\boldsymbol{b}\| \cos \theta
\end{align}
$$

</div>

これによって、 $n$ 次元ベクトルに対して2つの形で内積が定義できました。\
実は、ここまでの間にコサイン類似度についても出てきているのですがそれについては後で話します。

[目次へ戻る:back:](#目次)

[前提知識の一覧に戻る:back:](#prerequisite-knowledge)

### 埋め込み表現

人間が日常生活の中でコミュニケーションなどのために使用している言語のことを、プログラミング言語や数学で用いられる論理式などと区別するために自然言語と呼ばれることがあります。数式やコンピューターで自然言語を処理する際には、何らかの形で数値に落とし込まなければなりません。一般的には成分が実数のベクトルを用いて自然言語を表します。これを埋め込み表現や分散表現といいます。\
単語の埋め込み表現としては下記のものが知られています。

- One-hotベクトル
- Word2Vec（[arXiv](https://arxiv.org/abs/1301.3781)、[Google](https://code.google.com/archive/p/word2vec/)）
- fastText（[arXiv_1](https://arxiv.org/abs/1607.04606)、[arXiv_2](https://arxiv.org/abs/1607.01759)、[Meta](https://research.facebook.com/downloads/fasttext/)、[GitHub](https://github.com/facebookresearch/fastText)）
- Glove（[PDF](https://nlp.stanford.edu/pubs/glove.pdf)、[GitHub](https://github.com/stanfordnlp/GloVe)）

文章の埋め込み表現では下記のものが知られています。

- BoW
- 単語の埋め込み表現の平均
- Doc2Vec（[arXiv](https://arxiv.org/abs/1607.05368)）
- WRD（[arXiv](https://arxiv.org/abs/2004.15003)）
- LASER（[GitHub](https://github.com/facebookresearch/LASER)）
- Universal Sentence Encoder（[arXiv](https://arxiv.org/abs/1803.11175)）
- InferSent（[arXiv](https://arxiv.org/abs/1705.02364)、[GitHub](https://github.com/facebookresearch/InferSent)、[Meta](https://research.facebook.com/downloads/infersent/)）
- Sentence BERT（[arXiv](https://arxiv.org/abs/1908.10084)）

[目次へ戻る:back:](#目次)

[前提知識の一覧に戻る:back:](#prerequisite-knowledge)

### コサイン類似度

コサイン類似度 $\text{cosine-similarity}$ は2つのベクトルがどの程度似ているのかを $-1 \leq \text{cosine-similarity} \leq 1$ で測るためのものです。定義は下記のとおりです。

$$
\text{let } \boldsymbol{a,b} \in \mathbb{R}^n \text{ },\text{ } \|\boldsymbol{a}\|\neq 0 \text{ },\text{ } \|\boldsymbol{b}\|\neq 0
$$

$$
\text{cosine-similarity}=\frac{\boldsymbol{a} \cdot \boldsymbol{b}}{\|\boldsymbol{a}\| \|\boldsymbol{a}\|}
$$

これは $n$ 次元ベクトルのノルムや三角関数の $\cos$ を使用した内積の定義を[証明](#cosine-similarity)した時に見た形と同じです。すなわち次の等式が成り立ちます。

$$
\exists\theta\in\mathbb{R},
$$

$$
\begin{align}
  \text{cosine-similarity} &= \frac{\boldsymbol{a} \cdot \boldsymbol{b}}{\|\boldsymbol{a}\| \|\boldsymbol{a}\|}\\
  &= \cos \theta
\end{align}
$$

これを満たす $\theta$ を求めるのは現実的に難しいことから、そのままのコサイン類似度の値を使用して2つのベクトルの類似度を測ります。 $\cos$ の単位円を用いた定義から $\theta$ を2つのベクトルのなす角だとすると、コサイン類似度の値が1に近いほど2つのベクトルは同じ方向を向いており、-1に近いほど真逆の方向を向いていると考えられます。\
一般的に、埋め込み表現とコサイン類似度を用いて単語や文章の類似度を測ります。

[目次へ戻る:back:](#目次)

[前提知識の一覧に戻る:back:](#prerequisite-knowledge)
