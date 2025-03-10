import os
import unittest
from unittest.mock import patch, Mock

from kisho_michelin import ReviewScraper


class TestKishoMichelin(unittest.TestCase):
    """棋書ミシュランスクレイパーのテストクラス"""

    def setUp(self):
        """テスト用のスクレイパーインスタンスを作成"""
        self.scraper = ReviewScraper()
        
    def load_test_data(self, filename):
        """テストデータファイルを読み込む"""
        filepath = os.path.join('test_data', filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    @patch('requests.get')
    def test_extract_links(self, mock_get):
        """リンク抽出機能のテスト"""
        # Mock the response of requests.get
        mock_response = Mock()
        mock_response.content = self.load_test_data('link_list.html')
        mock_get.return_value = mock_response

        expected_links = [
            "https://rocky-and-hopper.sakura.ne.jp/Kisho-Michelin/1/1-1.htm",
            "https://rocky-and-hopper.sakura.ne.jp/Kisho-Michelin/2/2-2.htm",
            "https://rocky-and-hopper.sakura.ne.jp/Kisho-Michelin/3/3-3.htm"
        ]

        links = self.scraper.extract_links()
        self.assertEqual(links, expected_links)

    @patch('requests.get')
    def test_parse_review_pages(self, mock_get):
        """ページ解析機能のテスト"""
        test_cases = [
            {
                'filename': 'review_page_1.html',
                'expected_data': {
                    "書名": "Book Title",
                    "著者": "Author Name",
                    "総合評価": "A",
                    "戦法": ["居飛車"],
                    "発行年月": "2021年8月",
                    "URL": "https://example.com/review"
                }
            },
            {
                'filename': 'review_page_2.html',
                'expected_data': {
                    "書名": "第61期将棋名人戦",
                    "著者": "毎日新聞社",
                    "総合評価": "D",
                    "戦法": ["居飛車"],
                    "発行年月": "2003年7月",
                    "URL": "https://example.com/review"
                }
            },
            {
                'filename': 'review_page_3.html',
                'expected_data': {
                    "書名": "週将ブックス 二段の力",
                    "著者": "週刊将棋",
                    "総合評価": "C",
                    "戦法": ["四間飛車"],
                    "発行年月": "2007年12月",
                    "URL": "https://example.com/review"
                }
            },
            {
                'filename': 'review_page_4.html',
                'expected_data': {
                    "書名": "秘法巻之参 大覇道伝説",
                    "著者": "週刊将棋",
                    "総合評価": "C",
                    "戦法": ["四間飛車"],
                    "発行年月": "1991年9月",
                    "URL": "https://example.com/review"
                }
            },
            {
                'filename': 'review_page_5.html',
                'expected_data': {
                    "書名": "マイナビ将棋BOOKS 一撃！対振り飛車へなちょこ急戦",
                    "著者": "Sugar",
                    "総合評価": "A",
                    "戦法": ['四間飛車', '三間飛車', '振り飛車', '中飛車', '居飛車'],
                    "発行年月": "2024年4月",
                    "URL": "https://example.com/review"
                }
            },
            {
                'filename': 'review_page_6.html',
                'expected_data': {
                    "書名": "入門詰将棋100題",
                    "著者": "佐瀬勇次",
                    "総合評価": "C",
                    "戦法": ["中飛車"],
                    "発行年月": "1980年8月",
                    "URL": "https://example.com/review"
                }
            },
            {
                'filename': 'review_page_7.html',
                'expected_data': {
                    "書名": "最強将棋21 現代調の将棋の研究",
                    "著者": "羽生善治",
                    "総合評価": "S",
                    "戦法": ['振り飛車', '居飛車'],
                    "発行年月": "2021年5月",
                    "URL": "https://example.com/review"
                }
            },
        ]

        for case in test_cases:
            with self.subTest(filename=case['filename']):
                # Mock the response of requests.get
                mock_response = Mock()
                mock_response.text = self.load_test_data(case['filename'])
                mock_get.return_value = mock_response

                url = "https://example.com/review"
                expected_data = case['expected_data']

                data = self.scraper.parse_review_page(url)
                self.assertEqual(data["書名"], expected_data["書名"])
                self.assertEqual(data["著者"], expected_data["著者"])
                self.assertEqual(data["総合評価"], expected_data["総合評価"])
                self.assertCountEqual(data["戦法"], expected_data["戦法"])
                self.assertEqual(data["発行年月"], expected_data["発行年月"])
                self.assertEqual(data["URL"], expected_data["URL"])


if __name__ == "__main__":
    unittest.main()