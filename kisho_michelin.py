# coding: utf-8
import requests
from bs4 import BeautifulSoup
import csv
import re
import time
from urllib.parse import urljoin

BASE_URL = "https://rocky-and-hopper.sakura.ne.jp/Kisho-Michelin/serial-number.htm"


def extract_links():
    response = requests.get(BASE_URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # 相対URLが「数字/数字-ハイフン.htm」形式の場合にマッチ
        if re.search(r"\d+/[\d-]+\.htm$", href):
            full_url = urljoin(BASE_URL, href)
            print(f"Matched link: {full_url}")
            links.append(full_url)

    print(f"Extracted {len(links)} links.")
    return links


def parse_review_page(url):
    time.sleep(1.2)
    response = requests.get(url)
    response.raise_for_status()

    # Shift_JIS でエンコーディングを指定
    response.encoding = "shift_jis"
    soup = BeautifulSoup(response.text, "html.parser")

    data = {
        "書名": "",
        "著者": "",
        "総合評価": "",
        "戦法": [],
        "発行年月": "",
        # "難易度": "",
        "URL": url,  # 後で Excel 用ハイパーリンクに組み込み
    }

    # -------------------------------------------------
    # 1) 書名の取得
    # -------------------------------------------------
    # タイトルパターン1: colspan="2"を持つtdの中のstrong
    title_tag = soup.find(lambda tag: tag.name == "td" and tag.get("colspan") == "2" and tag.find("strong"))
    if title_tag:
        # 書籍タイトルの前にシリーズ名などがある場合（「週将ブックス」など）
        title_parts = []
        for string in title_tag.stripped_strings:
            title_parts.append(string)
        title_text = " ".join(title_parts)
        title_text = re.sub(r"^\s*■\s*", "", title_text)
        title_text = re.sub(r"\s+", " ", title_text).strip()
        data["書名"] = title_text
    else:
        # タイトルパターン2: 単純なstrong
        title_tag = soup.find("strong")
        if title_tag:
            title_text = title_tag.get_text(strip=True) or ""
            title_text = re.sub(r"^\s*■\s*", "", title_text)
            title_text = re.sub(r"\s+", " ", title_text).strip()
            data["書名"] = title_text
        # タイトルパターン3: 特定のテーブル構造の中のstrong
        else:
            title_td = soup.find(lambda tag: tag.name == "td" and tag.get("bgcolor") == "#FFFFE6")
            if title_td and title_td.find("strong"):
                title_parts = []
                for string in title_td.stripped_strings:
                    title_parts.append(string)
                title_text = " ".join(title_parts)
                title_text = re.sub(r"^\s*■\s*", "", title_text)
                title_text = re.sub(r"\s+", " ", title_text).strip()
                data["書名"] = title_text

    # -------------------------------------------------
    # 2) 著者の取得
    # -------------------------------------------------
    author_patterns = ["著者", "編", "編　者", "著　者", "監　修", "著"]
    author_found = False

    for pattern in author_patterns:
        if author_found:
            break
        # (A)パターン: <td>著者</td><td>○○</td>
        author_row = soup.find("td", string=lambda s: s and pattern in s)
        if author_row and author_row.find_next_sibling("td"):
            data["著者"] = author_row.find_next_sibling("td").get_text(strip=True)
            author_found = True
        else:
            # (B)パターン: "【著　者】" を厳密に探す
            alt_author_td = soup.find(
                lambda t: t.name == "td" and f"【{pattern}】" in t.get_text()
            )
            if alt_author_td:
                text_val = alt_author_td.get_text(strip=True)
                match = re.search(rf"【{pattern}】[：:、\s]*(.*)", text_val)
                if match:
                    author = re.sub(r"\s+", " ", match.group(1)).strip()
                    data["著者"] = author
                    author_found = True

    # -------------------------------------------------
    # 3) 発行年月の取得
    # -------------------------------------------------
    # (A)パターン: <td>発行年月</td><td>YYYY年M月</td>
    # (B)パターン: <td>発行：2021年8月</td>

    date_row = soup.find("td", string="発行年月")
    if date_row and date_row.find_next_sibling("td"):
        data["発行年月"] = date_row.find_next_sibling("td").get_text(strip=True)
    else:
        # (B)パターン: "発行：YYYY年M月" を含む <td>
        alt_date_td = soup.find(
            lambda t: t.name == "td" and "発行：" in t.get_text()
        )
        if alt_date_td:
            text_val = alt_date_td.get_text(strip=True)
            # 改行やスペースを整える
            text_val = re.sub(r"\s+", " ", text_val)
            date_match = re.search(r"発行：(.+)", text_val)
            if date_match:
                data["発行年月"] = date_match.group(1).strip()

    # -------------------------------------------------
    # 4) 総合評価/難易度の取得
    # -------------------------------------------------
    # 総合評価の取得 - 複数のパターンに対応
    # パターン1: [総合評価]をテキストに含むtd
    rating_td = soup.find(lambda tag: tag.name == "td" and "総合評価" in tag.get_text())
    if rating_td:
        strong_tag = rating_td.find("strong")
        if strong_tag:
            data["総合評価"] = strong_tag.get_text(strip=True)
        else:
            # [総合評価]の後の値を取得
            rating_text = rating_td.get_text(strip=True)
            match = re.search(r'\[?総合評価[^\w]*([A-Z]+)', rating_text)
            if match:
                data["総合評価"] = match.group(1)

    # パターン2: 総合評価という文字列を含むtd
    if not data["総合評価"]:
        alt_rating_td = soup.find(lambda tag: tag.name == "td" and "総合評価" in tag.get_text())
        if alt_rating_td:
            next_td = alt_rating_td.find_next_sibling("td")
            if next_td:
                data["総合評価"] = next_td.get_text(strip=True)
            else:
                # 同じセル内に値がある場合
                rating_text = alt_rating_td.get_text(strip=True)
                match = re.search(r'総合評価[：:]*\s*([A-Z]+)', rating_text)
                if match:
                    data["総合評価"] = match.group(1)

    # パターン3: 特定の構造のテーブル内
    if not data["総合評価"]:
        # Lambda関数内でのNoneチェックが必要
        rating_row = soup.find("tr", lambda tag: tag is not None and tag.find("td", bgcolor="#DFFFDF") is not None and "総合評価" in tag.text)
        if rating_row:
            strong_tag = rating_row.find("strong")
            if strong_tag:
                data["総合評価"] = strong_tag.get_text(strip=True)

    # -------------------------------------------------
    # 5) 戦法の抽出
    # -------------------------------------------------
    strategies = []
    strategy_patterns = ["居飛車", "振り飛車", "四間飛車", "三間飛車", "中飛車", "角換わり", "横歩取り"]

    for pattern in strategy_patterns:
        if soup.find(lambda tag: tag.name == "td" and tag.string and pattern in tag.string):
            strategies.append(pattern)

    # 戦法がtd内に含まれていない場合、全テキストから検索
    if not strategies:
        content = soup.get_text()
        strategies = re.findall(r"居飛車|振り飛車|四間飛車|三間飛車|中飛車|角換わり|横歩取り", content)

    data["戦法"] = list(set(strategies))

    print(f"Parsed data from {url}: {data}")
    return data


def main():
    try:
        links = extract_links()
    except requests.RequestException as e:
        print(f"Error fetching links: {e}")
        return

    # 1) 出力を TSV に変更
    #    Python のcsv.writerで delimiter="\t" を指定するだけ

    # URL列を削除し、書名をリンクに
    # Excel用ハイパーリンク式: =HYPERLINK("URL","書名")

    with open("kisho_reviews.tsv", "w", newline="", encoding="utf-8-sig") as f:
        # CSVモジュールでTSVとして書き出すため delimiter="\t" を指定
        fieldnames = ["書名", "総合評価", "戦法", "著者", "発行年月"]
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            delimiter="\t"
        )
        writer.writeheader()

        for link in links:
            try:
                data = parse_review_page(link)

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

            except requests.RequestException as e:
                print(f"Network error processing {link}: {e}")
            except Exception as e:
                print(f"Error processing {link}: {e}")

if __name__ == "__main__":
    main()
