# 🎯 ポテンシャル営業先アタックリスト作成エージェント

AIが公開情報をもとに「今の営業先以外の有望マーケット」を発見し、具体企業リストを生成します。

---

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を開いて `ANTHROPIC_API_KEY` を設定してください：

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
APP_USERNAME=admin
APP_PASSWORD=password123
```

### 3. アプリ起動

```bash
# Windows
start.bat

# または直接
streamlit run app.py
```

ブラウザで http://localhost:8501 を開いてください。

---

## 使い方

| ステップ | 内容 |
|----------|------|
| ① ログイン | ユーザー名・パスワードで認証 |
| ② 情報入力 | 会社名・サービス名・強み・ターゲット業界を入力 |
| ③ 業界ヒートマップ | 3C分析（Customer/Competitor/Company）でスコアリング・可視化 |
| ④ アタックリスト | 具体企業名・売上規模・スコア付きリストをExcel/CSVで出力 |

---

## プロジェクト構成

```
├── app.py                      # メインエントリポイント
├── pages/
│   ├── 1_🔐_ログイン.py
│   ├── 2_📝_情報入力.py
│   ├── 3_🌡️_業界ヒートマップ.py
│   └── 4_📋_アタックリスト.py
├── src/
│   ├── agent/claude_agent.py   # Claude API 呼び出し・3C分析・企業生成
│   ├── data_fetcher/           # robots.txt準拠Webスクレイパー
│   ├── parser/                 # HTML解析・企業情報抽出
│   ├── scorer/                 # スコアリングエンジン
│   └── output/                 # Excel / CSV 出力
├── config/
│   ├── settings.py             # 設定（重み・APIキー・スクレイピング設定）
│   └── industries.py           # 業界リスト
├── utils/
│   ├── logger.py               # ログ出力
│   └── rate_limiter.py         # レート制限
├── logs/                       # 日次ログファイル（自動生成）
├── output/                     # Excel/CSV出力先（自動生成）
├── .env                        # 環境変数（要作成）
├── requirements.txt
└── start.bat                   # Windows起動スクリプト
```

---

## スコアリングロジック

### 業界スコア（3C分析）

| 観点 | 項目 | 重み |
|------|------|------|
| **Customer** | 市場規模・実績伸び率・将来伸び率・市場ニーズ | 40% |
| **Competitor** | 競合数・競合強度・市場余地 | 30% |
| **Company** | 解決策適合・実績親和性・リソース適合 | 30% |

### 企業スコア（ICP/フィット/競合）

| 観点 | 重み |
|------|------|
| ICP適合度（業種・規模・BM） | 40% |
| ソリューションフィット感 | 35% |
| 競合飽和度（低い=高スコア） | 25% |

---

## 注意事項・免責

- 本ツールが生成する企業情報・スコアは **AI推定値** です
- 売上規模等の数値には「（推定）」と明示されます
- スクレイピングは各サイトの `robots.txt` および利用規約に従います
- 個人情報は扱わず、法人単位の公開情報のみを対象とします
- 最終的な営業判断は必ず人間が行ってください
