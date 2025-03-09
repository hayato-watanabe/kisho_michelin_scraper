import unittest
from unittest.mock import patch, Mock
import kisho_michelin
import os

class TestKishoMichelin(unittest.TestCase):

    def load_test_data(self, filename):
        filepath = os.path.join('test_data', filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    @patch('kisho_michelin.requests.get')
    def test_extract_links(self, mock_get):
        # Mock the response of requests.get
        mock_response = Mock()
        mock_response.content = self.load_test_data('link_list.html')
        mock_get.return_value = mock_response

        expected_links = [
            "https://rocky-and-hopper.sakura.ne.jp/Kisho-Michelin/1/1-1.htm",
            "https://rocky-and-hopper.sakura.ne.jp/Kisho-Michelin/2/2-2.htm",
            "https://rocky-and-hopper.sakura.ne.jp/Kisho-Michelin/3/3-3.htm"
        ]

        links = kisho_michelin.extract_links()
        self.assertEqual(links, expected_links)

    @patch('kisho_michelin.requests.get')
    def test_parse_review_page_1(self, mock_get):
        # Mock the response of requests.get
        mock_response = Mock()
        mock_response.text = self.load_test_data('review_page_1.html')
        mock_get.return_value = mock_response

        url = "https://example.com/review"
        expected_data = {
            "書名": "Book Title",
            "著者": "Author Name",
            "総合評価": "A",
            "戦法": ["居飛車"],
            "発行年月": "2021年8月",
            "URL": url
        }

        data = kisho_michelin.parse_review_page(url)
        self.assertEqual(data, expected_data)

    @patch('kisho_michelin.requests.get')
    def test_parse_review_page_2(self, mock_get):
        # Mock the response of requests.get
        mock_response = Mock()
        mock_response.text = self.load_test_data('review_page_2.html')
        mock_get.return_value = mock_response

        url = "https://example.com/review"
        expected_data = {
            "書名": "第61期将棋名人戦",
            "著者": "毎日新聞社",
            "総合評価": "D",
            "戦法": ["居飛車"],
            "発行年月": "2003年7月",
            "URL": url
        }

        data = kisho_michelin.parse_review_page(url)
        self.assertEqual(data, expected_data)

    @patch('kisho_michelin.requests.get')
    def test_parse_review_page_3(self, mock_get):
        # Mock the response of requests.get
        mock_response = Mock()
        mock_response.text = self.load_test_data('review_page_3.html')
        mock_get.return_value = mock_response

        url = "https://example.com/review"
        expected_data = {
            "書名": "週将ブックス 二段の力",
            "著者": "週刊将棋",
            "総合評価": "C",
            "戦法": ["四間飛車"],
            "発行年月": "2007年12月",
            "URL": url
        }

        data = kisho_michelin.parse_review_page(url)
        self.assertEqual(data, expected_data)

    @patch('kisho_michelin.requests.get')
    def test_parse_review_page_4(self, mock_get):
        # Mock the response of requests.get
        mock_response = Mock()
        mock_response.text = self.load_test_data('review_page_4.html')
        mock_get.return_value = mock_response

        url = "https://example.com/review"
        expected_data = {
            "書名": "秘法巻之参 大覇道伝説",
            "著者": "週刊将棋",
            "総合評価": "C",
            "戦法": ["四間飛車"],
            "発行年月": "1991年9月",
            "URL": url
        }

        data = kisho_michelin.parse_review_page(url)
        self.assertEqual(data, expected_data)

    @patch('kisho_michelin.requests.get')
    def test_parse_review_page_5(self, mock_get):
        # Mock the response of requests.get
        mock_response = Mock()
        mock_response.text = self.load_test_data('review_page_5.html')
        mock_get.return_value = mock_response

        url = "https://example.com/review"
        expected_data = {
            "書名": "マイナビ将棋BOOKS 一撃！対振り飛車へなちょこ急戦",
            "著者": "Sugar",
            "総合評価": "A",
            "戦法": ["四間飛車"],
            "発行年月": "2024年4月",
            "URL": url
        }

        data = kisho_michelin.parse_review_page(url)
        self.assertEqual(data, expected_data)

    @patch('kisho_michelin.requests.get')
    def test_parse_review_page_6(self, mock_get):
        # Mock the response of requests.get
        mock_response = Mock()
        mock_response.text = self.load_test_data('review_page_6.html')
        mock_get.return_value = mock_response

        url = "https://example.com/review"
        expected_data = {
            "書名": "入門詰将棋100題",
            "著者": "佐瀬勇次",
            "総合評価": "C",
            "戦法": ["中飛車"],
            "発行年月": "1980年8月",
            "URL": url
        }

        data = kisho_michelin.parse_review_page(url)
        self.assertEqual(data, expected_data)

    @patch('kisho_michelin.requests.get')
    def test_parse_review_page_7(self, mock_get):
        # Mock the response of requests.get
        mock_response = Mock()
        mock_response.text = self.load_test_data('review_page_7.html')
        mock_get.return_value = mock_response

        url = "https://example.com/review"
        expected_data = {
            "書名": "最強将棋21 現代調の将棋の研究",
            "著者": "羽生善治",
            "総合評価": "S",
            "戦法": ["中飛車"],
            "発行年月": "2021年5月",
            "URL": url
        }

        data = kisho_michelin.parse_review_page(url)
        self.assertEqual(data, expected_data)

if __name__ == "__main__":
    unittest.main()
