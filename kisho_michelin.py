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
        "難易度": "",
        "URL": url,  # 後で Excel 用ハイパーリンクに組み込み
    }

    # -------------------------------------------------
    # 1) 書名の取得
    # -------------------------------------------------
    # 書名の取得
    title_tag = soup.find(lambda tag: tag.name == "td" and tag.get("colspan") == "2" and tag.find("strong"))
    if title_tag:
        # Concatenate any preceding text with the strong tag text
        title_text = title_tag.get_text(separator=" ", strip=True)
        title_text = re.sub(r"^\s*■\s*", "", title_text)
        title_text = re.sub(r"\s+", " ", title_text).strip()
        data["書名"] = title_text
    else:
        # Additional check for book title in a different structure
        title_tag = soup.find("strong")
        if title_tag:
            title_text = title_tag.get_text() or ""
            title_text = re.sub(r"^\s*■\s*", "", title_text)
            title_text = re.sub(r"\s+", " ", title_text).strip()
            data["書名"] = title_text

    # -------------------------------------------------
    # 2) 著者の取得
    # -------------------------------------------------
    # 著者の取得
    author_patterns = ["著者", "編", "編　者", "監　修", "著"]
    author_found = False

    for pattern in author_patterns:
        if author_found:
            break
        # (A)パターン: <td>著者</td><td>○○</td>
        author_row = soup.find("td", string=pattern)
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
    # 総合評価の取得
    # Further improved 総合評価の取得
    rating_td = soup.find(lambda tag: tag.name == "td" and "[総合評価]" in tag.get_text())
    if rating_td:
        strong_tag = rating_td.find("strong")
        data["総合評価"] = strong_tag.get_text(strip=True) if strong_tag else rating_td.get_text(strip=True).split("］")[-1].strip()
    else:
        alt_rating_td = soup.find(lambda tag: tag.name == "td" and "総合評価" in tag.get_text())
        if alt_rating_td:
            next_td = alt_rating_td.find_next_sibling("td")
            data["総合評価"] = next_td.get_text(strip=True) if next_td else alt_rating_td.get_text(strip=True).split("：")[-1].strip()

    # Further improved 難易度の取得
    difficulty_td = soup.find(lambda t: t.name == "td" and "難易度" in t.get_text())
    if difficulty_td:
        next_td = difficulty_td.find_next_sibling("td")
        data["難易度"] = next_td.get_text(strip=True) if next_td else difficulty_td.get_text(strip=True).split("：")[-1].strip()
    else:
        alt_difficulty_td = soup.find(lambda tag: tag.name == "td" and "難易度" in tag.get_text())
        if alt_difficulty_td:
            next_td = alt_difficulty_td.find_next_sibling("td")
            data["難易度"] = next_td.get_text(strip=True) if next_td else alt_difficulty_td.get_text(strip=True).split("：")[-1].strip()

    # -------------------------------------------------
    # 5) 戦法の抽出
    # -------------------------------------------------
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
        fieldnames = ["書名", "総合評価", "戦法", "著者", "発行年月", "難易度"]
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
                    "難易度": data["難易度"],
                }

                writer.writerow(row_dict)

            except requests.RequestException as e:
                print(f"Network error processing {link}: {e}")
            except Exception as e:
                print(f"Error processing {link}: {e}")

if __name__ == "__main__":
    main()
