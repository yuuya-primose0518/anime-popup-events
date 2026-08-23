# アニメ POP UP イベント情報

全国のアニメ・マンガ関連ポップアップストア／期間限定ショップの開催情報をまとめた静的サイトです。

- **一覧** — 開催中／開催予定／終了で切り替え、地域・並び替え・フリーワード検索
- **カレンダー** — 月間グリッド。日付をクリックするとその日に開催中のイベントを表示
- **作品から探す** — 作品ごとの開催履歴（過去分含む）
- 各イベントに会場の Google マップリンク

## 構成

```
.
├── index.html                    ← ページの骨組み（データは持たない・118行）
├── assets/style.css              ← 見た目
├── assets/app.js                 ← data/events.json を読み込んで描画する
├── data/events.json              ← データ本体。イベントの更新はここだけ
├── build_site.py                 ← 公開用 _site/ を組み立てる（JSON-LD・sitemap）
├── make_og.py                    ← OGP画像 og.png を生成（Playwright が必要）
├── og.png                        ← OGP画像
└── .github/workflows/deploy.yml  ← push すると GitHub Pages へ自動デプロイ
```

データは HTML に埋め込みません。`assets/app.js` が実行時に `data/events.json` を
`fetch` して描画します。**イベント情報を更新するときに触るのは `data/events.json` だけ**で、
`index.html` の差分は発生しません。

外部ライブラリ・CDN への依存はありません。

## 更新のしかた

1. `data/events.json` にイベントを追記する
2. commit して push する → GitHub Actions が自動でビルド・デプロイする

ビルドを手元で走らせる必要はありません。`build_site.py` がやるのは
「検索エンジン向けの味付け」だけです。

- `index.html` の `<!-- BUILD:JSONLD:START -->` 〜 `END` の間に schema.org の
  JSON-LD（イベント全件）を差し込む
- `sitemap.xml` / `robots.txt` を生成する
- 以上をまとめて `_site/` に出力する（**リポジトリ内のファイルは書き換えない**）

## ローカルで確認する

`fetch` を使うため、`index.html` を `file://` でそのまま開くと動きません。
かならずHTTPサーバ経由で開いてください。

```bash
python3 -m http.server 8000                 # → http://localhost:8000/
```

公開されるものと同じ状態（JSON-LD・sitemap 入り）を見たいときは:

```bash
python3 build_site.py
python3 -m http.server -d _site 8000
```

`SITE_URL` を渡すと canonical / OGP / sitemap の絶対URLを差し替えられます。
GitHub Actions では Pages の公開URLが自動で入るため、手で設定する必要はありません。

```bash
SITE_URL=https://<ユーザー名>.github.io/<リポジトリ名> python3 build_site.py
```

## デザインを直したいとき

- 色・レイアウト → `assets/style.css`
- 表示ロジック（カード・カレンダー・絞り込み） → `assets/app.js`
- 見出し・フッター・メタ情報 → `index.html`

## データ形式

```jsonc
{
  "meta": { "updated": "YYYY-MM-DD" },
  "events": [
    {
      "id": "一意のスラッグ",
      "work": "作品名",              // 作品別ページのグルーピングキー。表記を統一すること
      "title": "イベント正式名称",
      "venue": "会場名（フロア等含む・表示用）",
      "pref": "都道府県",            // 全国巡回は「全国」
      "region": "関東",              // 北海道|東北|関東|中部|関西|中国|四国|九州・沖縄|全国
      "start": "YYYY-MM-DD",
      "end":   "YYYY-MM-DD",
      "url":    "公式/詳細ページURL",
      "source": "情報の出典URL",
      "tags": ["少年", "マルイ"],
      "map": [ { "n": "表示名", "q": "Googleマップ検索クエリ" } ]
    }
  ]
}
```

開催状況（開催中／開催予定／終了）は `start` と `end` から表示時に自動判定するため、データには持たせません。過去のイベントは削除せずアーカイブとして残します。

### `map` のルール

- 単一会場 → 要素1つ（「地図で見る」リンクになる）
- 複数会場が明示されている → 会場ごとに要素を分ける（会場名ごとのリンクになる）
- 「全国◯店舗」など**会場が特定できないものは空配列 `[]`** にする。推測で店舗を補わないこと
- 同名店舗が多い場合は `q` に地名を足して一意にする（例: `"栄ロフト 名古屋"`）。フロア表記は入れない

## 出典

掲載情報は [コラボカフェ](https://collabo-cafe.com/events/category/pop-up-store/)、[AMNIBUS](https://event.amnibus.com/)、[アニメイトタイムズ](https://www.animatetimes.com/) および各作品公式サイトの公開情報をもとにまとめています。最新の開催状況・入場方法は必ず公式サイトをご確認ください。
