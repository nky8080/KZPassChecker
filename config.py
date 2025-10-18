"""設定ファイル"""
import os

# AWS設定
REGION = "us-west-2"
MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

# 文化の森お出かけパス公式サイト
ODEKAKE_PASS_URL = "https://odekakepass.hot-ishikawa.jp/"

# 文化の森お出かけパス対象施設（公式サイトから取得した正確な18施設）
FACILITIES = {
    "鈴木大拙館": {
        "url": "https://www.kanazawa-museum.jp/daisetz/",
        "regular_closed": ["月曜日"],  # 月曜日定休（祝日の場合は翌平日）
        "selector": ".news, .info, .notice",
        "phone": "076-221-8011",
        "address": "石川県金沢市本多町3-4-20",
        "special_pages": [
            "https://www.kanazawa-museum.jp/daisetz/date.html",  # iframe休館日情報（最重要）
            "http://www.kanazawa-museum.jp/pdf/closed.pdf",  # 展示日程PDF
            "https://www.kanazawa-museum.jp/daisetz/news.html"   # お知らせ
        ],
        "iframe_pages": [
            "https://www.kanazawa-museum.jp/daisetz/date.html"  # 詳細休館日情報iframe
        ],
        "notes": "詳細休館日情報はiframe(date.html)に記載。SSL設定が古いため特別な接続設定が必要。"
    },
    "金沢21世紀美術館": {
        "url": "https://www.kanazawa21.jp/",
        "regular_closed": [],
        "selector": ".news, .info, .notice",
        "phone": "076-220-2800",
        "address": "石川県金沢市広坂1-2-1",
        "special_pages": [
            "https://www.kanazawa21.jp/data_list.php?g=7&d=1"  # 休館日カレンダー
        ]
    },
    "いしかわ生活工芸ミュージアム": {
        "url": "https://www.ishikawa-densankan.jp/",
        "regular_closed": [],
        "selector": ".news, .info",
        "phone": "076-262-2020",
        "address": "石川県の伝統工芸品36種を一堂に展示"
    },
    "武家屋敷跡 野村家": {
        "url": "https://www.nomurake.com/",  # Googleマップではなく公式サイト
        "regular_closed": [],
        "selector": ".news, .info",
        "phone": "076-221-3553",
        "address": "石川県金沢市長町1-3-32"
    },
    "国指定重要文化財 成巽閣": {
        "url": "https://www.seisonkaku.com/",  # 公式サイト
        "regular_closed": [],
        "selector": ".news, .info",
        "phone": "076-221-0580",
        "address": "石川県金沢市兼六町1-2"
    },
    "石川県立歴史博物館": {
        "url": "https://ishikawa-rekihaku.jp/info/index.html",
        "regular_closed": [],
        "selector": ".news, .info, .notice, .calendar, table",
        "phone": "076-262-3236",
        "address": "石川県金沢市出羽町3-1"
    },
    "国立工芸館": {
        "url": "https://www.momat.go.jp/craft-museum/",
        "regular_closed": [],
        "selector": ".news, .info, .notice",
        "phone": "050-5541-8600",
        "address": "石川県金沢市出羽町3-2"
    },
    "特別名勝 兼六園": {
        "url": "http://www.pref.ishikawa.jp/siro-niwa/kenrokuen/",
        "regular_closed": [],
        "selector": ".news, .info",
        "phone": "076-234-3800",
        "address": "石川県金沢市兼六町1-2"
    },
    "金沢城公園": {
        "url": "http://www.pref.ishikawa.jp/siro-niwa/kanazawajou/",
        "regular_closed": [],
        "selector": ".news, .info",
        "phone": "076-234-3800",
        "address": "石川県金沢市丸の内1-1"
    },
    "前田土佐守家資料館": {
        "url": "https://www.kanazawa-museum.jp/maedatosa/",
        "regular_closed": ["月曜日"],  # 月曜日定休（祝日の場合は開館）
        "selector": ".news, .info",
        "phone": "076-233-1561",
        "address": "石川県金沢市片町2-10-17",
        "notes": "月曜日定休（祝日の場合は開館）。10月の休館日はサイトに記載の日付のみ。"
    },
    "金沢市老舗記念館": {
        "url": "https://www.kanazawa-museum.jp/shinise/",
        "regular_closed": [],
        "selector": ".news, .info",
        "phone": "076-220-2524",
        "address": "石川県金沢市長町2-2-45"
    },
    "石川県立美術館": {
        "url": "https://www.ishibi.pref.ishikawa.jp/guide/hours/",
        "regular_closed": [],
        "selector": ".news, .info, .notice, h4",
        "phone": "076-231-7580",
        "address": "石川県金沢市出羽町2-1"
    },
    "金沢くらしの博物館": {
        "url": "https://www.kanazawa-museum.jp/minzoku/index.html",
        "regular_closed": [],
        "selector": ".news, .info",
        "phone": "076-222-5740",
        "address": "石川県金沢市飛梅町3-31"
    },
    "金沢能楽美術館": {
        "url": "https://www.kanazawa-noh-museum.gr.jp/",
        "regular_closed": [],
        "selector": ".news, .info",
        "phone": "076-220-2790",
        "address": "石川県金沢市広坂1-2-25",
        "special_pages": [
            "https://www.kanazawa-noh-museum.gr.jp/reservation/"  # 予約状況・休館日カレンダー
        ]
    },
    "金沢市立中村記念美術館": {
        "url": "https://www.kanazawa-museum.jp/nakamura/",
        "regular_closed": [],
        "selector": ".news, .info",
        "phone": "076-221-0751",
        "address": "石川県金沢市本多町3-2-29"
    },
    "加賀本多博物館": {
        "url": "http://honda-museum.jp/",
        "regular_closed": [],
        "selector": ".news, .info",
        "phone": "076-261-0500",
        "address": "石川県金沢市出羽町3-1"
    },
    "金沢ふるさと偉人館": {
        "url": "https://www.kanazawa-museum.jp/ijin/",
        "regular_closed": [],
        "selector": ".news, .info",
        "phone": "076-220-2474",
        "address": "石川県金沢市下本多町6-18-4"
    },
    "石川四高記念文化交流館": {
        "url": "https://www.pref.ishikawa.jp/shiko-kinbun/",
        "regular_closed": [],
        "selector": ".news, .info",
        "phone": "076-262-5464",
        "address": "石川県金沢市広坂2-2-5"
    }
}

# スクレイピング設定
REQUEST_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"