# coding: utf-8
"""
将棋書籍の書評サイト「棋書ミシュラン」からデータを抽出するスクレイパー
https://rocky-and-hopper.sakura.ne.jp/Kisho-Michelin/serial-number.htm
"""
import csv
import logging
import re
import time
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

# 定数設定
BASE_URL = "https://rocky-and-hopper.sakura.ne.jp/Kisho-Michelin/serial-number.htm"
OUTPUT_FILE = "kisho_reviews.tsv"
REQUEST_DELAY = 1.2  # スクレイピング間隔（秒）
ENCODING = "shift_jis"  # サイトのエンコーディング

# 抽出対象の戦法リスト
STRATEGY_PATTERNS = ["居飛車", "振り飛車", "四間飛車", "三間飛車", "中飛車", "角換わり", "横歩取り"]

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


class ReviewScraper:
    """棋書ミシュランの書評データを抽出するスクレイパークラス"""

    def __init__(self, base_url: str = BASE_URL, delay: float = REQUEST_DELAY):
        """
        初期化
        
        Args:
            base_url: スクレイピング対象のベースURL
            delay: リクエスト間の遅延時間（秒）
        """
        self.base_url = base_url
        self.delay = delay
        
    def extract_links(self) -> List[str]:
        """
        トップページから書評ページへのリンクを抽出する
        
        Returns:
            書評ページのURLリスト
        """
        try:
            response = self._make_request(self.base_url)
            soup = BeautifulSoup(response.content, "html.parser")
            
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                # 相対URLが「数字/数字-ハイフン.htm」形式の場合にマッチ
                if re.search(r"\d+/[\d-]+\.htm$", href):
                    full_url = urljoin(self.base_url, href)
                    logger.debug(f"Matched link: {full_url}")
                    links.append(full_url)
            
            logger.info(f"Extracted {len(links)} links.")
            return links
            
        except requests.RequestException as e:
            logger.error(f"Error fetching links from {self.base_url}: {e}")
            raise
    
    def parse_review_page(self, url: str) -> Dict[str, Union[str, List[str]]]:
        """
        書評ページから情報を抽出する
        
        Args:
            url: 書評ページのURL
            
        Returns:
            抽出したデータの辞書
        """
        time.sleep(self.delay)  # サーバー負荷軽減のための遅延
        
        try:
            response = self._make_request(url, encoding=ENCODING)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 初期データ構造
            data = {
                "書名": "",
                "著者": "",
                "総合評価": "",
                "戦法": [],
                "発行年月": "",
                "URL": url,
            }
            
            # 各要素を抽出
            data["書名"] = self._extract_title(soup)
            data["著者"] = self._extract_author(soup)
            data["発行年月"] = self._extract_publication_date(soup)
            data["総合評価"] = self._extract_rating(soup)
            data["戦法"] = self._extract_strategies(soup)
            
            logger.info(f"Parsed data from {url}")
            logger.debug(f"Extracted data: {data}")
            return data
            
        except requests.RequestException as e:
            logger.error(f"Network error processing {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error processing {url}: {str(e)}", exc_info=True)
            raise
    
    def save_to_tsv(self, data_list: List[Dict[str, Union[str, List[str]]]], output_file: str = OUTPUT_FILE) -> None:
        """
        抽出したデータをTSVファイルに保存する
        
        Args:
            data_list: 書評データのリスト
            output_file: 出力ファイル名
        """
        fieldnames = ["書名", "総合評価", "戦法", "著者", "発行年月"]
        
        try:
            with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=fieldnames,
                    delimiter="\t",
                    quoting=csv.QUOTE_NONE,
                    escapechar='\\'
                )
                writer.writeheader()
                
                for data in data_list:
                    # 書名をExcel用のハイパーリンク式に
                    hyperlinked_name = f'=HYPERLINK("{data["URL"]}","{data["書名"]}")'
                    
                    row_dict = {
                        "書名": hyperlinked_name,
                        "総合評価": data["総合評価"],
                        "戦法": ", ".join(data["戦法"]),
                        "著者": data["著者"],
                        "発行年月": data["発行年月"],
                    }
                    
                    writer.writerow(row_dict)
                    
            logger.info(f"Successfully saved {len(data_list)} reviews to {output_file}")
                
        except (IOError, OSError) as e:
            logger.error(f"Error saving to file {output_file}: {e}")
            raise
    
    def _make_request(self, url: str, encoding: Optional[str] = None) -> requests.Response:
        """
        指定されたURLにリクエストを送信する
        
        Args:
            url: リクエスト対象のURL
            encoding: レスポンスのエンコーディング（指定がある場合）
            
        Returns:
            HTTP応答オブジェクト
        """
        response = requests.get(url)
        response.raise_for_status()
        
        if encoding:
            response.encoding = encoding
            
        return response
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        ページから書籍タイトルを抽出する
        
        Args:
            soup: BeautifulSoupオブジェクト
            
        Returns:
            書籍タイトル
        """
        # パターン1: colspan="2"を持つtdの中のstrong
        title_tag = soup.find(lambda tag: tag.name == "td" and tag.get("colspan") == "2" and tag.find("strong"))
        if title_tag:
            return self._clean_title_text(title_tag)
            
        # パターン2: 単純なstrong
        title_tag = soup.find("strong")
        if title_tag:
            return self._clean_title_text(title_tag)
            
        # パターン3: 特定のテーブル構造の中のstrong
        title_td = soup.find(lambda tag: tag.name == "td" and tag.get("bgcolor") == "#FFFFE6")
        if title_td and title_td.find("strong"):
            return self._clean_title_text(title_td)
            
        return ""
    
    def _clean_title_text(self, tag: Tag) -> str:
        """
        タグから取得したテキストをクリーンアップする
        
        Args:
            tag: BeautifulSoup Tagオブジェクト
            
        Returns:
            クリーンアップされたテキスト
        """
        title_parts = []
        for string in tag.stripped_strings:
            title_parts.append(string)
            
        title_text = " ".join(title_parts)
        title_text = re.sub(r"^\s*■\s*", "", title_text)
        title_text = re.sub(r"\s+", " ", title_text).strip()
        return title_text
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """
        ページから著者名を抽出する
        
        Args:
            soup: BeautifulSoupオブジェクト
            
        Returns:
            著者名
        """
        # パターン1: "【著　者】" を含むtd
        author_td = soup.find("td", string=re.compile(r"【著\s*者】"))
        if author_td:
            author_text = author_td.get_text(strip=True)
            match = re.search(r"【著\s*者】\s*(.+)", author_text)
            if match:
                return match.group(1).strip()
        
        # パターン2: 複数の著者表記パターンに対応
        author_patterns = ["著者", "編", "編　者", "著　者", "監　修", "著"]
        
        for pattern in author_patterns:
            # (A)パターン: <td>著者</td><td>○○</td>
            author_row = soup.find("td", string=lambda s: s and pattern in s)
            if author_row and author_row.find_next_sibling("td"):
                return author_row.find_next_sibling("td").get_text(strip=True)
                
            # (B)パターン: "【著　者】" を厳密に探す
            alt_author_td = soup.find(
                lambda t: t.name == "td" and f"【{pattern}】" in t.get_text()
            )
            if alt_author_td:
                text_val = alt_author_td.get_text(strip=True)
                match = re.search(rf"【{pattern}】[：:、\s]*(.*)", text_val)
                if match:
                    return re.sub(r"\s+", " ", match.group(1)).strip()
                    
        return ""
    
    def _extract_publication_date(self, soup: BeautifulSoup) -> str:
        """
        ページから発行年月を抽出する
        
        Args:
            soup: BeautifulSoupオブジェクト
            
        Returns:
            発行年月
        """
        # パターン1: <td>発行年月</td><td>YYYY年M月</td>
        date_row = soup.find("td", string="発行年月")
        if date_row and date_row.find_next_sibling("td"):
            return date_row.find_next_sibling("td").get_text(strip=True)
            
        # パターン2: "発行：YYYY年M月" を含む <td>
        alt_date_td = soup.find(
            lambda t: t.name == "td" and "発行：" in t.get_text()
        )
        if alt_date_td:
            text_val = alt_date_td.get_text(strip=True)
            # 改行やスペースを整える
            text_val = re.sub(r"\s+", " ", text_val)
            date_match = re.search(r"発行：(.+)", text_val)
            if date_match:
                return date_match.group(1).strip()
                
        return ""
    
    def _extract_rating(self, soup: BeautifulSoup) -> str:
        """
        ページから総合評価を抽出する
        
        Args:
            soup: BeautifulSoupオブジェクト
            
        Returns:
            総合評価
        """
        # パターン1: [総合評価]をテキストに含むtd内のstrong
        rating_td = soup.find(lambda tag: tag.name == "td" and "総合評価" in tag.get_text())
        if rating_td:
            strong_tag = rating_td.find("strong")
            if strong_tag:
                return strong_tag.get_text(strip=True)
                
            # [総合評価]の後の値を取得
            rating_text = rating_td.get_text(strip=True)
            match = re.search(r'\[?総合評価[^\w]*([A-Z]+)', rating_text)
            if match:
                return match.group(1)
        
        # パターン2: 総合評価という文字列を含むtdの次のtd
        alt_rating_td = soup.find(lambda tag: tag.name == "td" and "[総合評価]" in tag.get_text())
        if alt_rating_td:
            next_td = alt_rating_td.find_next_sibling("td")
            if next_td:
                return next_td.get_text(strip=True)
                
            # 同じセル内に値がある場合
            rating_text = alt_rating_td.get_text(strip=True)
            match = re.search(r'総合評価[：:]*\s*([A-Z]+)', rating_text)
            if match:
                return match.group(1)
        
        # パターン3: 特定の構造のテーブル内
        rating_row = soup.find("tr", lambda tag: tag is not None and tag.find("td", bgcolor="#DFFFDF") is not None and "総合評価" in tag.text)
        if rating_row:
            strong_tag = rating_row.find("strong")
            if strong_tag:
                return strong_tag.get_text(strip=True)
                
        return ""
    
    def _extract_strategies(self, soup: BeautifulSoup) -> List[str]:
        """
        ページから戦法情報を抽出する
        
        Args:
            soup: BeautifulSoupオブジェクト
            
        Returns:
            戦法のリスト
        """
        strategies = []
        
        # td内に戦法名が含まれるか検索
        for pattern in STRATEGY_PATTERNS:
            if soup.find(lambda tag: tag.name == "td" and tag.string and pattern in tag.string):
                strategies.append(pattern)
        
        # 戦法がtd内に含まれていない場合、全テキストから検索
        if not strategies:
            content = soup.get_text()
            strategies = re.findall(r"居飛車|振り飛車|四間飛車|三間飛車|中飛車|角換わり|横歩取り", content)
        
        return list(set(strategies))  # 重複を除去


def main():
    """メイン実行関数"""
    scraper = ReviewScraper()
    
    try:
        # リンク一覧を取得
        links = scraper.extract_links()
        
        # 各ページからデータを抽出
        all_data = []
        for link in links:
            try:
                data = scraper.parse_review_page(link)
                all_data.append(data)
            except Exception as e:
                logger.error(f"Skipping {link} due to error: {e}")
                continue
        
        # 結果をTSVファイルに保存
        scraper.save_to_tsv(all_data)
        
    except Exception as e:
        logger.critical(f"Program stopped with error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)