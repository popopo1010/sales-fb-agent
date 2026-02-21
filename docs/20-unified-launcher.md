# CA FB + RA FB 一括起動

CA（初回面談）とRA（初回架電）の両方のFBシステムを、1コマンドで起動する方法。

## 前提

- **sales-fb-agent**（CA FB）と **RA_FBシステム**（RA FB）の両方がセットアップ済み
- RA_FBシステムのパス: `/Users/ikeobook15/RA_FBシステム`（デフォルト）

## 起動方法

```bash
cd sales-fb-agent
./scripts/start_all_fb.sh
```

または:

```bash
bash scripts/start_all_fb.sh
```

## 動作

| システム | コマンド | 投稿先 |
|----------|----------|--------|
| CA FB | `/fb` | #dk_ca_初回面談fb |
| RA FB | `/rafb_call` | #dk_ra_初回架電fb |
| RA FB | `/rafb_mtg` | 法人面談FB（CA法人） |

両方が起動したら、Slack で `/fb`、`/rafb_call`、`/rafb_mtg` が使えます。

## 終了

`Ctrl+C` で両方のプロセスを終了します。

## RA_FBシステムのパスを変更する場合

環境変数 `RA_FB_PATH` で指定できます。

```bash
RA_FB_PATH=/path/to/RA_FBシステム ./scripts/start_all_fb.sh
```

## トラブルシューティング

| 現象 | 対処 |
|------|------|
| `RA_FBシステム が見つかりません` | `RA_FB_PATH` で正しいパスを指定する |
| 片方だけ起動しない | 各システムを個別に起動してエラーを確認 |
| CA のみ起動したい | `python -m src.slack_app` を直接実行 |
| RA のみ起動したい | `cd RA_FBシステム && python scripts/slack_server.py` |
