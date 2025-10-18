"""施設情報スクレイピング機能"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil.parser import parse
import re
from typing import Dict, List, Optional
import logging
import boto3
import json
from config import FACILITIES, REQUEST_TIMEOUT, USER_AGENT, REGION, MODEL_ID

logger = logging.getLogger(__name__)

class FacilityScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # SSL設定を緩和
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # SSL/TLS設定を追加
        import ssl
        from requests.adapters import HTTPAdapter
        from urllib3.util.ssl_ import create_urllib3_context
        
        class SSLAdapter(HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                context = create_urllib3_context()
                context.set_ciphers('DEFAULT@SECLEVEL=1')
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                # 古いTLSバージョンも許可（鈴木大拙館対応）
                try:
                    context.minimum_version = ssl.TLSVersion.TLSv1
                except:
                    pass  # 古いPythonバージョンでは無視
                kwargs['ssl_context'] = context
                return super().init_poolmanager(*args, **kwargs)
        
        self.session.mount('https://', SSLAdapter())
        self.session.verify = False
        
        # Bedrock クライアントの初期化
        try:
            self.bedrock_client = boto3.client('bedrock-runtime', region_name=REGION)
        except Exception as e:
            logger.warning(f"Bedrock client initialization failed: {e}")
            self.bedrock_client = None
    
    def get_facility_closure_info(self, facility_name: str, target_date: str) -> Dict:
        """指定施設の休館情報を取得"""
        if facility_name not in FACILITIES:
            return {"error": f"施設 '{facility_name}' は対象外です"}
        
        facility_info = FACILITIES[facility_name]
        
        try:
            # 対象日付をパース
            target_dt = parse(target_date)
            
            # レギュラー休館日チェック
            weekday_jp = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
            target_weekday = weekday_jp[target_dt.weekday()]
            
            # 施設固有の休館日判定
            is_regular_closed = self._check_regular_closure(facility_name, target_dt, target_weekday)
            
            # 公式サイトから臨時休館情報を取得（施設名も渡す）
            special_closure_info = self._scrape_special_closures(
                facility_info["url"], 
                facility_info["selector"],
                target_dt,
                facility_name  # 施設名を追加
            )
            
            return {
                "facility": facility_name,
                "date": target_date,
                "weekday": target_weekday,
                "is_regular_closed": is_regular_closed,
                "regular_closed_days": facility_info["regular_closed"],
                "special_closures": special_closure_info,
                "is_closed": is_regular_closed or special_closure_info["has_closure"],
                "closure_reason": self._get_closure_reason(is_regular_closed, special_closure_info)
            }
            
        except Exception as e:
            logger.error(f"Error getting closure info for {facility_name}: {e}")
            return {"error": f"情報取得エラー: {str(e)}"}
    
    def _check_regular_closure(self, facility_name: str, target_dt: datetime, target_weekday: str) -> bool:
        """施設固有の定休日判定"""
        if facility_name not in FACILITIES:
            return False
        
        facility_info = FACILITIES[facility_name]
        regular_closed_days = facility_info.get("regular_closed", [])
        
        # 設定された定休日をチェック
        if target_weekday in regular_closed_days:
            return True
        
        # 祝日の場合の特別処理（必要に応じて追加）
        # 現在は基本的な曜日ベースの判定のみ
        
        return False
    
    def _ai_analyze_closure_info(self, facility_name: str, scraped_text: str, target_date: datetime) -> Dict:
        """AIを使用して休館情報を解析"""
        if not self.bedrock_client:
            return {"ai_analysis": False, "error": "Bedrock client not available"}
        
        try:
            # 対象日付の情報
            target_date_str = target_date.strftime("%Y年%m月%d日")
            target_weekday = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"][target_date.weekday()]
            
            # AIに送信するプロンプト（改善版）
            prompt = f"""あなたは文化施設の開館・休館情報を正確に判定する専門家です。
以下の{facility_name}の公式サイト情報を基に、{target_date_str}（{target_weekday}）の開館状況を判定してください。

【判定対象】
施設名: {facility_name}
対象日: {target_date_str}（{target_weekday}）

【サイト情報】
{scraped_text[:4000]}

【判定基準】
1. 長期休館（工事・改修・リニューアル等）
   - 「令和7年9月から12月中旬まで工事のため休館」
   - 「改修工事により○月○日まで休館」
   
2. 定期休館日
   - 「毎週月曜日休館」「木曜日定休」等
   - 祝日の場合の振替休館
   
3. 臨時休館
   - 展示替え、設備点検、イベント準備等
   - 年末年始、特別な日程
   
4. 開館情報
   - 展示会・イベント開催中
   - 「本日開館」等の明示的な表現

【重要な注意点】
- 和暦（令和、平成）を西暦に正確に変換してください
- 期間表現（「○月から○月まで」「○月中旬」等）を正確に解釈してください
- 対象日が休館期間に含まれるかを慎重に判定してください
- 展示会等のイベントが開催されている場合は通常開館です
- 不明確な情報の場合は信頼度を下げてください

【回答形式】
以下のJSON形式で回答してください：
{{
    "is_closed": true/false,
    "reason": "具体的な休館理由（開館の場合は空文字）",
    "confidence": 0.0-1.0,
    "detected_info": "判定根拠となった具体的な情報",
    "analysis_details": "判定プロセスの詳細説明"
}}"""

            # Bedrock APIを呼び出し
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=MODEL_ID,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            ai_response = response_body['content'][0]['text']
            
            # JSONレスポンスを解析
            try:
                # JSONブロックを抽出
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    ai_result = json.loads(json_match.group())
                    return {
                        "ai_analysis": True,
                        "is_closed": ai_result.get("is_closed", False),
                        "reason": ai_result.get("reason", ""),
                        "confidence": ai_result.get("confidence", 0.0),
                        "detected_info": ai_result.get("detected_info", ""),
                        "analysis_details": ai_result.get("analysis_details", ""),
                        "raw_response": ai_response
                    }
                else:
                    return {
                        "ai_analysis": True,
                        "error": "JSON format not found in AI response",
                        "raw_response": ai_response
                    }
                    
            except json.JSONDecodeError as e:
                return {
                    "ai_analysis": True,
                    "error": f"JSON decode error: {e}",
                    "raw_response": ai_response
                }
                
        except Exception as e:
            logger.error(f"AI analysis error for {facility_name}: {e}")
            return {
                "ai_analysis": False,
                "error": str(e)
            }
    def _get_facility_specific_pages(self, facility_name: str) -> List[str]:
        """施設固有の特殊ページを取得"""
        specific_pages = []
        
        # 金沢21世紀美術館の特殊ページ
        if "金沢21世紀美術館" in facility_name:
            specific_pages.extend([
                "https://www.kanazawa21.jp/data_list.php?g=7&d=1",  # 休館日情報ページ
                "https://www.kanazawa21.jp/visit",  # 利用案内
                "https://www.kanazawa21.jp/news"    # ニュース
            ])
        
        # 金沢能楽美術館の特殊ページ
        elif "金沢能楽美術館" in facility_name:
            specific_pages.extend([
                "https://www.kanazawa-noh-museum.gr.jp/reservation/",  # 予約状況・休館日カレンダー
                "https://www.kanazawa-noh-museum.gr.jp/",  # メインページ
                "https://www.kanazawa-noh-museum.gr.jp/guide/"  # 利用案内
            ])
        
        # 鈴木大拙館の特殊ページ（iframe対応）
        elif "鈴木大拙館" in facility_name:
            specific_pages.extend([
                "https://www.kanazawa-museum.jp/daisetz/date.html",  # iframe休館日情報（最重要）
                "https://www.kanazawa-museum.jp/daisetz/news.html",  # お知らせ
                "https://www.kanazawa-museum.jp/daisetz/about.html"  # 基本情報
            ])
        
        # 鈴木大拙館の場合
        elif "鈴木大拙館" in facility_name:
            specific_pages.extend([
                "https://www.kanazawa-museum.jp/daisetz/",  # メインページ
                "https://www.kanazawa-museum.jp/daisetz/guide/",
                "https://www.kanazawa-museum.jp/daisetz/news/"
            ])
        
        # 石川県立歴史博物館の場合
        elif "石川県立歴史博物館" in facility_name:
            specific_pages.extend([
                "https://ishikawa-rekihaku.jp/info/index.html",  # 開館時間・料金・アクセス
                "https://ishikawa-rekihaku.jp/",
                "https://ishikawa-rekihaku.jp/news/"
            ])
        
        # 前田土佐守家資料館の場合
        elif "前田土佐守家資料館" in facility_name:
            specific_pages.extend([
                "https://www.kanazawa-museum.jp/maedatosa/",  # メインページ
                "https://www.kanazawa-museum.jp/maedatosa/guide/",
                "https://www.kanazawa-museum.jp/maedatosa/news/"
            ])
        
        # 石川県立美術館の場合
        elif "石川県立美術館" in facility_name:
            specific_pages.extend([
                "https://www.ishibi.pref.ishikawa.jp/guide/hours/",  # 開館時間・休館日
                "https://www.ishibi.pref.ishikawa.jp/guide/",
                "https://www.ishibi.pref.ishikawa.jp/news/"
            ])
        
        # 金沢ふるさと偉人館の場合
        elif "金沢ふるさと偉人館" in facility_name:
            specific_pages.extend([
                "https://www.kanazawa-museum.jp/ijin/guide/",
                "https://www.kanazawa-museum.jp/ijin/news/"
            ])
        
        # 国立工芸館の場合
        elif "国立工芸館" in facility_name:
            specific_pages.extend([
                "https://www.momat.go.jp/craft-museum/visit/",
                "https://www.momat.go.jp/craft-museum/news/"
            ])
        
        return specific_pages
    
    def _get_additional_pages(self, base_url: str, facility_name: str) -> List[str]:
        """施設固有の追加確認ページを取得"""
        additional_pages = []
        
        # まず施設固有の特殊ページを取得
        specific_pages = self._get_facility_specific_pages(facility_name)
        additional_pages.extend(specific_pages)
        
        # 一般的なページも追加（重複は除外）
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        
        potential_pages = [
            f"{base_url}/guide/",
            f"{base_url}/hours/",
            f"{base_url}/news/",
            f"{base_url}/info/",
            f"{base_url}/access/"
        ]
        
        # 重複を避けて追加
        for page in potential_pages:
            if page not in additional_pages:
                additional_pages.append(page)
        
        return additional_pages
    
    def _parse_daisetz_iframe_page(self, url: str, target_date: datetime) -> Dict:
        """鈴木大拙館のiframe休館日ページを専用解析"""
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                return {"error": f"Failed to access {url}"}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            full_text = soup.get_text()
            
            # 休館日情報を探す
            closure_info = {
                "has_specific_closure": False,
                "details": [],
                "raw_content": full_text[:1000],  # デバッグ用
                "iframe_found": True
            }
            
            target_month = target_date.month
            target_day = target_date.day
            target_year = target_date.year
            
            # 「休館日のご案内」セクションを検索
            if "休館日のご案内" in full_text:
                closure_info["iframe_found"] = True
                
                # 対象月の休館日を詳細解析
                month_patterns = {
                    10: r'10月\s*([^\n]+?)(?=\n11月|\nお知らせ)',
                    11: r'11月\s*([^\n]+?)(?=\n12月|\nお知らせ)',
                    12: r'12月\s*([^\n]+?)(?=\nお知らせ|$)'
                }
                
                if target_month in month_patterns:
                    import re
                    pattern = month_patterns[target_month]
                    match = re.search(pattern, full_text, re.DOTALL)
                    
                    if match:
                        month_text = match.group(1).strip()
                        
                        # 個別の日付をチェック（例: 14(火), 20(月)）
                        day_pattern = f'(?:^|,|\\s){target_day}\\('
                        if re.search(day_pattern, month_text):
                            closure_info["has_specific_closure"] = True
                            closure_info["details"].append({
                                "date": target_date.strftime("%Y-%m-%d"),
                                "reason": f"iframe休館日情報による休館（{target_month}月{target_day}日）",
                                "source": "iframe専用解析",
                                "confidence": 1.0,
                                "month_text": month_text
                            })
                        
                        # 範囲指定の場合の特別処理（まず範囲をチェック）
                        range_patterns = [
                            r'(\d+)\([^)]+\)-(\d+)\([^)]+\)'  # 4(土)-10(金)
                        ]
                        
                        range_found = False
                        for range_pattern in range_patterns:
                            range_matches = re.findall(range_pattern, month_text)
                            for start_day, end_day in range_matches:
                                start_day, end_day = int(start_day), int(end_day)
                                if start_day <= target_day <= end_day:
                                    closure_info["has_specific_closure"] = True
                                    closure_info["details"].append({
                                        "date": target_date.strftime("%Y-%m-%d"),
                                        "reason": f"iframe休館日情報による連続休館（{target_month}月{start_day}-{end_day}日）",
                                        "source": "iframe専用解析",
                                        "confidence": 1.0,
                                        "range_info": f"{start_day}-{end_day}"
                                    })
                                    range_found = True
                                    break
                            if range_found:
                                break
            
            return closure_info
            
        except Exception as e:
            logger.error(f"Error parsing Daisetz iframe page: {e}")
            return {"error": str(e)}
    
    def _parse_noh_museum_reservation_page(self, url: str, target_date: datetime) -> Dict:
        """金沢能楽美術館の予約状況ページを専用解析"""
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                return {"error": f"Failed to access {url}"}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            full_text = soup.get_text()
            
            # 休館日情報を探す
            closure_info = {
                "has_specific_closure": False,
                "details": [],
                "raw_content": full_text[:1000],  # デバッグ用
                "calendar_found": False
            }
            
            target_month = target_date.month
            target_day = target_date.day
            target_year = target_date.year
            
            # カレンダー要素を検索
            calendar_elements = soup.select('#calendar, .rsv-calendar, .rsv-tp-box-2')
            
            if calendar_elements:
                closure_info["calendar_found"] = True
                
                for calendar in calendar_elements:
                    calendar_text = calendar.get_text()
                    
                    # 対象月のカレンダーが表示されているかチェック
                    month_pattern = f"{target_year}年{target_month}月"
                    if month_pattern in calendar_text:
                        
                        # 対象日が「休館日」として表示されているかチェック
                        day_patterns = [
                            f"{target_day}休館日",
                            f"{target_day} 休館日",
                            f"休館日{target_day}",
                            f"休館日 {target_day}"
                        ]
                        
                        for pattern in day_patterns:
                            if pattern in calendar_text:
                                closure_info["has_specific_closure"] = True
                                closure_info["details"].append({
                                    "date": target_date.strftime("%Y-%m-%d"),
                                    "reason": f"予約カレンダーによる休館日（{target_month}月{target_day}日）",
                                    "source": "予約状況ページ解析",
                                    "confidence": 1.0,
                                    "calendar_text": calendar_text[:500]
                                })
                                break
                        
                        # 休館日でない場合は開館日として記録
                        if not closure_info["has_specific_closure"]:
                            # 対象日が数字として存在するかチェック（開館日の可能性）
                            day_exists_patterns = [
                                f" {target_day} ",
                                f">{target_day}<",
                                f"{target_day}日"
                            ]
                            
                            for pattern in day_exists_patterns:
                                if pattern in calendar_text:
                                    closure_info["details"].append({
                                        "date": target_date.strftime("%Y-%m-%d"),
                                        "reason": f"予約カレンダー確認済み：開館日（{target_month}月{target_day}日）",
                                        "source": "予約状況ページ解析",
                                        "confidence": 1.0,
                                        "is_open": True
                                    })
                                    break
                        
                        break  # 対象月が見つかったので終了
            
            # 全体テキストからも休館情報を検索
            closure_keywords = ["休館日", "休館", "臨時休館", "閉館"]
            for keyword in closure_keywords:
                if keyword in full_text:
                    # キーワード周辺のテキストを抽出
                    lines = full_text.split('\n')
                    for i, line in enumerate(lines):
                        if keyword in line and str(target_day) in line:
                            context_start = max(0, i-1)
                            context_end = min(len(lines), i+2)
                            context = '\n'.join(lines[context_start:context_end]).strip()
                            
                            closure_info["details"].append({
                                "keyword": keyword,
                                "context": context,
                                "line": line.strip(),
                                "source": "テキスト解析"
                            })
            
            return closure_info
            
        except Exception as e:
            logger.error(f"Error parsing Noh Museum reservation page: {e}")
            return {"error": str(e)}
    
    def _parse_kanazawa21_closure_page(self, url: str, target_date: datetime) -> Dict:
        """金沢21世紀美術館の休館日ページを専用解析"""
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                return {"error": f"Failed to access {url}"}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            full_text = soup.get_text()
            
            # 休館日情報を探す
            closure_info = {
                "has_specific_closure": False,
                "details": [],
                "raw_content": full_text[:1000],  # デバッグ用
                "closure_calendar_found": False
            }
            
            target_month = target_date.month
            target_day = target_date.day
            target_year = target_date.year
            
            # 「2025（令和7）年1月〜2026（令和8）年3月の休館日」セクションを検索
            if "2025（令和7）年1月〜2026（令和8）年3月の休館日" in full_text:
                closure_info["closure_calendar_found"] = True
                
                # テーブルから休館日を詳細解析
                tables = soup.find_all('table')
                
                for table in tables:
                    rows = table.find_all('tr')
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            month_cell = cells[0].get_text(strip=True)
                            dates_cell = cells[1].get_text(strip=True)
                            
                            # 対象月かチェック
                            month_patterns = [
                                f"{target_month}月",
                                f"{target_year}年{target_month}月"
                            ]
                            
                            if any(pattern in month_cell for pattern in month_patterns):
                                # この行が対象月の休館日情報
                                closure_info["details"].append({
                                    "month": target_month,
                                    "closure_dates_text": dates_cell,
                                    "source": "休館日カレンダー"
                                })
                                
                                # 対象日が休館日に含まれるかチェック
                                day_patterns = [
                                    f"{target_day}日",
                                    f" {target_day}日",
                                    f"/{target_day}日",
                                    f"{target_day}日("
                                ]
                                
                                for pattern in day_patterns:
                                    if pattern in dates_cell:
                                        closure_info["has_specific_closure"] = True
                                        closure_info["details"].append({
                                            "date": target_date.strftime("%Y-%m-%d"),
                                            "reason": f"休館日カレンダーによる休館（{target_month}月{target_day}日）",
                                            "source": "専用ページ解析",
                                            "confidence": 1.0,
                                            "calendar_text": dates_cell
                                        })
                                        break
                                
                                break  # 対象月が見つかったので終了
                
                # 臨時開館日・臨時休館日もチェック
                if "臨時開館日" in full_text or "臨時休館日" in full_text:
                    # 臨時開館日のパターン
                    temp_open_pattern = rf"臨時開館日.*?{target_year}年{target_month}月{target_day}日"
                    if re.search(temp_open_pattern, full_text):
                        # 臨時開館日の場合、休館判定を取り消し
                        closure_info["has_specific_closure"] = False
                        closure_info["details"].append({
                            "date": target_date.strftime("%Y-%m-%d"),
                            "reason": f"臨時開館日（{target_month}月{target_day}日）",
                            "source": "専用ページ解析",
                            "confidence": 1.0,
                            "special_note": "通常休館日だが臨時開館"
                        })
                    
                    # 臨時休館日のパターン
                    temp_close_pattern = rf"臨時休館日.*?{target_year}年{target_month}月{target_day}日"
                    if re.search(temp_close_pattern, full_text):
                        closure_info["has_specific_closure"] = True
                        closure_info["details"].append({
                            "date": target_date.strftime("%Y-%m-%d"),
                            "reason": f"臨時休館日（{target_month}月{target_day}日）",
                            "source": "専用ページ解析",
                            "confidence": 1.0,
                            "special_note": "通常開館日だが臨時休館"
                        })
            
            return closure_info
            
        except Exception as e:
            logger.error(f"Error parsing Kanazawa21 closure page: {e}")
            return {"error": str(e)}
    
    def _scrape_multiple_pages(self, urls: List[str], facility_name: str = "", target_date: datetime = None) -> str:
        """複数ページから情報を取得（施設固有の解析を含む）"""
        combined_text = ""
        special_analysis_results = []
        
        for url in urls:
            try:
                # 鈴木大拙館のiframe休館日ページの場合
                if ("kanazawa-museum.jp/daisetz/date.html" in url and 
                    "鈴木大拙館" in facility_name and 
                    target_date):
                    
                    special_result = self._parse_daisetz_iframe_page(url, target_date)
                    
                    # 特殊解析結果を保存
                    if special_result.get("has_specific_closure"):
                        special_analysis_results.extend([d for d in special_result["details"] if "date" in d])
                    elif special_result.get("iframe_found"):
                        # iframeが見つかったが対象日は休館日ではない場合
                        special_analysis_results.append({
                            "date": target_date.strftime("%Y-%m-%d"),
                            "reason": "iframe休館日情報確認済み：開館日",
                            "source": "iframe専用解析",
                            "confidence": 1.0,
                            "is_open": True
                        })
                    
                    # 通常のテキスト取得も行う
                    response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        text = soup.get_text()
                        combined_text += f"\n--- {url} (鈴木大拙館iframe解析済み) ---\n{text[:1500]}\n"
                
                # 金沢能楽美術館の予約状況ページの場合
                elif ("kanazawa-noh-museum.gr.jp/reservation" in url and 
                    "金沢能楽美術館" in facility_name and 
                    target_date):
                    
                    special_result = self._parse_noh_museum_reservation_page(url, target_date)
                    
                    # 特殊解析結果を保存
                    if special_result.get("has_specific_closure"):
                        special_analysis_results.extend([d for d in special_result["details"] if "date" in d])
                    elif special_result.get("calendar_found"):
                        # カレンダーが見つかったが対象日は休館日ではない場合
                        open_details = [d for d in special_result["details"] if d.get("is_open")]
                        if open_details:
                            special_analysis_results.extend(open_details)
                    
                    # 通常のテキスト取得も行う
                    response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        text = soup.get_text()
                        combined_text += f"\n--- {url} (能楽美術館専用解析済み) ---\n{text[:1500]}\n"
                
                # 金沢21世紀美術館の特殊ページの場合
                elif ("kanazawa21.jp/data_list.php" in url and 
                    "金沢21世紀美術館" in facility_name and 
                    target_date):
                    
                    special_result = self._parse_kanazawa21_closure_page(url, target_date)
                    
                    # 特殊解析結果を保存（休館・開館両方）
                    if special_result.get("has_specific_closure"):
                        special_analysis_results.extend([d for d in special_result["details"] if "date" in d])
                    elif special_result.get("closure_calendar_found"):
                        # カレンダーが見つかったが対象日は休館日ではない場合
                        special_analysis_results.append({
                            "date": target_date.strftime("%Y-%m-%d"),
                            "reason": "休館日カレンダー確認済み：開館日",
                            "source": "専用ページ解析",
                            "confidence": 1.0,
                            "is_open": True
                        })
                    
                    # 通常のテキスト取得も行う
                    response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        text = soup.get_text()
                        combined_text += f"\n--- {url} (特殊解析済み) ---\n{text[:1500]}\n"
                else:
                    # 通常のページ処理
                    response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        text = soup.get_text()
                        combined_text += f"\n--- {url} ---\n{text[:2000]}\n"
                        
            except Exception as e:
                logger.debug(f"Failed to fetch {url}: {e}")
                continue
        
        # 特殊解析結果をテキストに追加
        if special_analysis_results:
            combined_text += "\n--- 特殊解析結果 ---\n"
            for result in special_analysis_results:
                combined_text += f"検出: {result['reason']}\n"
        
        return combined_text
    
    def _get_manual_closure_info(self, facility_name: str, target_date: datetime) -> Dict:
        """手動で設定された重要な休館情報を取得"""
        manual_closures = {
            "金沢ふるさと偉人館": {
                "closure_period": {
                    "start": datetime(2025, 9, 1),
                    "end": datetime(2025, 12, 15),  # 12月中旬を15日と仮定
                    "reason": "令和7年9月から12月中旬（予定）まで、工事のため休館"
                }
            }
        }
        
        if facility_name in manual_closures:
            closure_info = manual_closures[facility_name]
            if "closure_period" in closure_info:
                period = closure_info["closure_period"]
                if period["start"] <= target_date <= period["end"]:
                    return {
                        "has_manual_closure": True,
                        "reason": period["reason"],
                        "confidence": 1.0,
                        "source": "手動設定（公式サイト情報）"
                    }
        
        return {"has_manual_closure": False}
    
    def _scrape_special_closures(self, url: str, selector: str, target_date: datetime, facility_name: str = "") -> Dict:
        """開館・休館情報をスクレイピング（定休日情報も含む）"""
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 全体のテキストから情報を取得
            full_text = soup.get_text()
            
            # 指定されたセレクタからも情報を取得
            news_elements = soup.select(selector)
            
            closure_info = {
                "has_closure": False,
                "details": [],
                "scraped_content": [],
                "site_status": "unknown"
            }
            
            # 開館・休館関連キーワード
            closure_keywords = ["休館", "休業", "臨時休館", "閉館", "休み", "定休"]
            open_keywords = ["開館", "営業", "本日開館", "開いて"]
            
            # 曜日ベースの定休日情報を検索
            weekday_patterns = [
                r'月曜日.*?休館',
                r'火曜日.*?休館', 
                r'水曜日.*?休館',
                r'木曜日.*?休館',
                r'金曜日.*?休館',
                r'土曜日.*?休館',
                r'日曜日.*?休館',
                r'休館.*?月曜日',
                r'定休.*?月曜日',
                r'定休.*?木曜日'
            ]
            
            # 対象日の曜日
            weekday_jp = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
            target_weekday = weekday_jp[target_date.weekday()]
            
            # サイト全体から定休日情報を検索
            for pattern in weekday_patterns:
                if re.search(pattern, full_text):
                    if target_weekday in pattern:
                        closure_info["has_closure"] = True
                        closure_info["details"].append({
                            "date": target_date.strftime("%Y-%m-%d"),
                            "reason": f"定休日（{target_weekday}）"
                        })
                        closure_info["site_status"] = "regular_closed"
                        break
            
            # 「本日開館」「本日休館」などの直接的な表現を検索
            today_patterns = [
                r'本日.*?開館',
                r'本日.*?休館',
                r'今日.*?開館',
                r'今日.*?休館'
            ]
            
            for pattern in today_patterns:
                match = re.search(pattern, full_text)
                if match:
                    matched_text = match.group()
                    if "開館" in matched_text and "休館" not in matched_text:
                        closure_info["site_status"] = "open_today"
                        closure_info["has_closure"] = False
                    elif "休館" in matched_text:
                        closure_info["has_closure"] = True
                        closure_info["site_status"] = "closed_today"
                        closure_info["details"].append({
                            "date": target_date.strftime("%Y-%m-%d"),
                            "reason": "本日休館"
                        })
                    break
            
            # ニュースエリアから特定日付の休館情報を検索
            for element in news_elements[:10]:
                text = element.get_text(strip=True)
                closure_info["scraped_content"].append(text[:200])
                
                if any(keyword in text for keyword in closure_keywords):
                    # 日付パターンを検索
                    date_patterns = [
                        r'(\d{1,2})月(\d{1,2})日',
                        r'(\d{4})年(\d{1,2})月(\d{1,2})日',
                        r'(\d{1,2})/(\d{1,2})',
                        r'(\d{4})/(\d{1,2})/(\d{1,2})'
                    ]
                    
                    for pattern in date_patterns:
                        matches = re.findall(pattern, text)
                        for match in matches:
                            try:
                                if len(match) == 2:
                                    month, day = int(match[0]), int(match[1])
                                    closure_date = datetime(target_date.year, month, day)
                                elif len(match) == 3:
                                    if '/' in pattern:
                                        year, month, day = int(match[0]), int(match[1]), int(match[2])
                                    else:
                                        year, month, day = int(match[0]), int(match[1]), int(match[2])
                                    closure_date = datetime(year, month, day)
                                else:
                                    continue
                                
                                if closure_date.date() == target_date.date():
                                    closure_info["has_closure"] = True
                                    closure_info["details"].append({
                                        "date": closure_date.strftime("%Y-%m-%d"),
                                        "reason": text[:100]
                                    })
                                    
                            except (ValueError, TypeError):
                                continue
            
            # 追加ページから情報を取得（施設固有の解析を含む）
            additional_pages = self._get_additional_pages(url, facility_name)
            additional_text = self._scrape_multiple_pages(additional_pages, facility_name, target_date)
            
            # 全テキストを結合
            combined_text = full_text + additional_text
            
            # AI解析を実行（より多くの情報を使用）
            ai_analysis = self._ai_analyze_closure_info(
                facility_name,
                combined_text,
                target_date
            )
            
            closure_info["ai_analysis"] = ai_analysis
            
            # 特殊解析結果を統合（最優先）
            special_closure_detected = False
            special_open_detected = False
            
            # additional_textから特殊解析結果を抽出
            if "鈴木大拙館iframe解析済み" in additional_text:
                # iframe解析結果を直接確認
                lines = additional_text.split('\n')
                for line in lines:
                    if "iframe休館日情報による" in line and "休館" in line:
                        closure_info["has_closure"] = True
                        closure_info["site_status"] = "iframe_detected_closed"
                        closure_info["details"].append({
                            "date": target_date.strftime("%Y-%m-%d"),
                            "reason": "iframe休館日情報による確定休館",
                            "confidence": 1.0,
                            "source": "iframe専用解析"
                        })
                        special_closure_detected = True
                        break
            elif "特殊解析結果" in additional_text:
                lines = additional_text.split('\n')
                for line in lines:
                    if "休館日カレンダーによる休館" in line:
                        closure_info["has_closure"] = True
                        closure_info["site_status"] = "calendar_detected_closed"
                        closure_info["details"].append({
                            "date": target_date.strftime("%Y-%m-%d"),
                            "reason": "休館日カレンダーによる確定休館",
                            "confidence": 1.0,
                            "source": "専用ページ解析"
                        })
                        special_closure_detected = True
                        break
                    elif "予約カレンダーによる休館日" in line:
                        closure_info["has_closure"] = True
                        closure_info["site_status"] = "reservation_calendar_closed"
                        closure_info["details"].append({
                            "date": target_date.strftime("%Y-%m-%d"),
                            "reason": "予約カレンダーによる確定休館",
                            "confidence": 1.0,
                            "source": "予約状況ページ解析"
                        })
                        special_closure_detected = True
                        break
                    elif "iframe休館日情報による" in line:
                        closure_info["has_closure"] = True
                        closure_info["site_status"] = "iframe_detected_closed"
                        closure_info["details"].append({
                            "date": target_date.strftime("%Y-%m-%d"),
                            "reason": "iframe休館日情報による確定休館",
                            "confidence": 1.0,
                            "source": "iframe専用解析"
                        })
                        special_closure_detected = True
                        break
                    elif "休館日カレンダー確認済み：開館日" in line:
                        closure_info["site_status"] = "calendar_detected_open"
                        special_open_detected = True
                        break
                    elif "予約カレンダー確認済み：開館日" in line:
                        closure_info["site_status"] = "reservation_calendar_open"
                        special_open_detected = True
                        break
                    elif "iframe休館日情報確認済み：開館日" in line:
                        closure_info["site_status"] = "iframe_detected_open"
                        special_open_detected = True
                        break
            
            # AI解析結果を統合（特殊解析がない場合のみ）
            if not special_closure_detected and not special_open_detected:
                if ai_analysis.get("ai_analysis") and ai_analysis.get("confidence", 0) > 0.7:
                    if ai_analysis.get("is_closed"):
                        closure_info["has_closure"] = True
                        closure_info["site_status"] = "ai_detected_closed"
                        closure_info["details"].append({
                            "date": target_date.strftime("%Y-%m-%d"),
                            "reason": ai_analysis.get("reason", "AI検出による休館"),
                            "confidence": ai_analysis.get("confidence", 0),
                            "detected_info": ai_analysis.get("detected_info", "")
                        })
                    elif not closure_info["has_closure"]:
                        # 正規表現で休館が検出されず、AIが開館と判定した場合
                        closure_info["site_status"] = "ai_detected_open"
            elif special_open_detected:
                # 特殊解析で開館が確定した場合、他の休館判定を上書き
                closure_info["has_closure"] = False
                if closure_info["site_status"] == "reservation_calendar_open":
                    closure_info["details"] = [{
                        "date": target_date.strftime("%Y-%m-%d"),
                        "reason": "予約カレンダー確認済み：開館日",
                        "confidence": 1.0,
                        "source": "予約状況ページ解析"
                    }]
                elif closure_info["site_status"] == "iframe_detected_open":
                    closure_info["details"] = [{
                        "date": target_date.strftime("%Y-%m-%d"),
                        "reason": "iframe休館日情報確認済み：開館日",
                        "confidence": 1.0,
                        "source": "iframe専用解析"
                    }]
                else:
                    closure_info["details"] = [{
                        "date": target_date.strftime("%Y-%m-%d"),
                        "reason": "休館日カレンダー確認済み：開館日",
                        "confidence": 1.0,
                        "source": "専用ページ解析"
                    }]
            
            return closure_info
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            
            # サイトアクセスに失敗した場合、手動設定の休館情報をチェック
            manual_info = self._get_manual_closure_info(facility_name, target_date)
            
            if manual_info["has_manual_closure"]:
                return {
                    "has_closure": True,
                    "details": [{
                        "date": target_date.strftime("%Y-%m-%d"),
                        "reason": manual_info["reason"],
                        "confidence": manual_info["confidence"],
                        "source": manual_info["source"]
                    }],
                    "error": str(e),
                    "site_status": "manual_override",
                    "ai_analysis": {
                        "ai_analysis": True,
                        "is_closed": True,
                        "reason": manual_info["reason"],
                        "confidence": manual_info["confidence"],
                        "detected_info": f"手動設定による情報: {manual_info['reason']}",
                        "analysis_details": f"サイトアクセスエラーのため手動設定情報を使用。{manual_info['source']}"
                    }
                }
            else:
                return {
                    "has_closure": False,
                    "details": [],
                    "error": str(e),
                    "site_status": "error"
                }
    
    def _get_closure_reason(self, is_regular_closed: bool, special_info: Dict) -> str:
        """休館理由を取得"""
        reasons = []
        
        if is_regular_closed:
            reasons.append("定休日")
        
        if special_info["has_closure"]:
            for detail in special_info["details"]:
                if "confidence" in detail:
                    # AI解析または手動設定による結果
                    confidence = detail["confidence"]
                    reason = detail["reason"]
                    source = detail.get("source", "AI検出")
                    reasons.append(f"{source} (信頼度{confidence:.1f}): {reason}")
                else:
                    # 正規表現による結果
                    reasons.append(f"臨時休館: {detail['reason']}")
        
        # AI解析で開館と判定された場合の情報も追加
        ai_analysis = special_info.get("ai_analysis", {})
        if (ai_analysis.get("ai_analysis") and 
            not special_info["has_closure"] and 
            ai_analysis.get("confidence", 0) > 0.7):
            reasons.append(f"AI判定 (信頼度{ai_analysis.get('confidence', 0):.1f}): 開館予定")
        
        return " / ".join(reasons) if reasons else "開館予定"
    
    def get_all_facilities_status(self, target_date: str) -> List[Dict]:
        """全施設の休館状況を取得"""
        results = []
        
        for facility_name in FACILITIES.keys():
            result = self.get_facility_closure_info(facility_name, target_date)
            results.append(result)
        
        return results