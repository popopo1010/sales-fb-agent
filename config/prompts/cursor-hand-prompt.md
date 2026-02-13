# Cursor 手動FB生成用プロンプト（API不要）

以下のプロンプトを Cursor チャットに貼り、書き起こしを添えて実行してください。  
生成されたFBをコピーして #dk_ca_fb に貼り付ければ完了です。

---

## プロンプト（コピー用）

```
以下の書き起こしを、@reference/pss と @reference/operations の
PSS・オペレーションマニュアルに沿って評価し、
@config/fb_format.md で定義された8項目の形式でフィードバックを出力してください。

---

【書き起こし】
（ここに書き起こしを貼り付ける）

---
```

---

## 使い方

1. 上記の「【書き起こし】」の部分に、初回面談の書き起こしを貼り付ける
2. 送信前に参照を紐づける:
   - `@reference/pss` と `@reference/operations` と `@config/fb_format.md`
   - `work` がルートの場合: `@sales-fb-agent/config/fb_format.md` 等
3. CursorがFBを生成する
4. 出力をコピーして Slack の #dk_ca_fb に貼り付ける

**APIキー・Slack設定は不要です。**
