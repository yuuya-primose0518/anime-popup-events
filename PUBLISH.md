# GitHub Pages で公開する手順

このフォルダはそのまま GitHub リポジトリになっています（`git init` 済み・初回コミット済み）。
以下の手順で公開できます。所要 5〜10 分程度です。

---

## 1. GitHub でリポジトリを作る

ブラウザで https://github.com/new を開き、以下を設定します。

| 項目 | 値 |
|---|---|
| Repository name | `anime-popup-events`（好きな名前でOK。URLに入ります） |
| Public / Private | **Public**（Private だと無料プランでは Pages が使えません） |
| Add a README file | **チェックしない** |
| .gitignore / license | **どちらも None** |

「Create repository」を押します。README等を追加しないのは、こちらに既にファイルがあるためです。

---

## 2. push する

ターミナルでこのフォルダに移動して、GitHub が表示しているリポジトリURLを使います。

```bash
cd ~/Documents/anime-popup-events

# <ユーザー名> と <リポジトリ名> を自分のものに置き換える
git remote add origin https://github.com/<ユーザー名>/<リポジトリ名>.git
git branch -M main
git push -u origin main
```

認証を求められたら、パスワード欄には**GitHubのログインパスワードではなく Personal Access Token** を入れます（GitHub は 2021 年にパスワード認証を廃止しています）。

- トークン作成：https://github.com/settings/tokens?type=beta →「Generate new token」
- Repository access: **Only select repositories** → 作ったリポジトリだけを選ぶ
- Permissions → Repository permissions → **Contents: Read and write**
- 有効期限は短め（90日など）でかまいません

macOS なら一度入力すればキーチェーンに保存されます。GitHub CLI (`brew install gh` → `gh auth login`) を使うともう少し楽です。

---

## 3. GitHub Pages を有効にする

リポジトリの **Settings → Pages** を開き、

- **Source: GitHub Actions** を選ぶ

これだけです。`Deploy from a branch` ではなく **GitHub Actions** を選んでください。このリポジトリには `.github/workflows/deploy.yml` が入っているので、push するたびに自動でビルド・デプロイされます。

Source を切り替えた時点でワークフローが走ります。**Actions** タブで進行を確認できます（1〜2分）。

---

## 4. 公開URLを確認する

デプロイが緑になったら、以下のURLで公開されています。

```
https://<ユーザー名>.github.io/<リポジトリ名>/
```

Settings → Pages の上部にもURLが表示されます。

> 反映まで初回は数分かかることがあります。表示がおかしいときはスーパーリロード（`Cmd + Shift + R`）を試してください。

---

## 5.（任意）独自ドメイン

独自ドメインを使う場合は Settings → Pages → Custom domain にドメインを入れ、DNS 側に以下を設定します。

- サブドメイン（`popup.example.com` など）→ CNAME レコードを `<ユーザー名>.github.io` に向ける
- ルートドメイン（`example.com`）→ A レコードを GitHub Pages の 4 つの IP に向ける

設定後「Enforce HTTPS」にチェックを入れます。証明書の発行に最大 24 時間かかることがあります。

---

## 週次の自動更新をサイトに反映する

毎週月曜 10:00（JST）の定期タスクが新着イベントを調べてデータを更新しています。これを公開サイトにも自動反映するには、定期タスクがリポジトリに push できる必要があります。

### 方式A：定期タスクから直接 push する（自動・推奨）

上の手順2で作ったのと同じ要領で、**このリポジトリだけにスコープを絞った** fine-grained token を用意します。

- Repository access: **Only select repositories** → このリポジトリのみ
- Permissions: **Contents: Read and write** のみ（他は付けない）

このトークンを Claude のプロジェクトに保存すれば、定期タスクが毎週

1. 新着イベントを調査して `data/events.json` を更新
2. `build_site.py` で `index.html` を再生成
3. commit して push → GitHub Actions がデプロイ

まで自動で行います。

**トレードオフを正直に書いておきます。** プロジェクトに保存したトークンは、そのプロジェクトを開ける人なら読めます。スコープを1リポジトリの Contents だけに絞ってあれば、最悪の場合でも「このサイトの中身を書き換えられる」以上のことは起きません（公開サイトなので情報漏洩にはあたりません）。それでも気になる場合は方式Bにしてください。有効期限を90日などにしておき、切れたら作り直すのが無難です。

準備ができたらリポジトリのURLとトークンを教えてください。定期タスクの手順に push を組み込みます。

### 方式B：手動で反映する（トークン不要）

定期タスクはこれまで通り更新済みの `events.json` と `index.html` を送るだけにして、反映は自分のタイミングで行います。

```bash
cd ~/Documents/anime-popup-events
# 送られてきた events.json を data/ に上書きしてから
python3 build_site.py
git add -A && git commit -m "イベント情報を更新" && git push
```

push すれば GitHub Actions が自動でデプロイします。

---

## 困ったときは

| 症状 | 対処 |
|---|---|
| Actions が赤くなる | Actions タブでログを見る。多くは Settings → Pages の Source が `GitHub Actions` になっていないケース |
| 404 が出る | Pages の有効化直後は数分かかる。URL末尾のスラッシュも確認 |
| CSSが当たらない・表示が崩れる | スーパーリロード（`Cmd + Shift + R`）。それでも直らなければ Actions のログで `Assemble _site` が成功しているか確認 |
| push で認証に失敗する | パスワードではなく Personal Access Token を使う。`git remote -v` でURLも確認 |
