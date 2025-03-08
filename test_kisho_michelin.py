import unittest
from unittest.mock import patch, Mock
import kisho_michelin

class TestKishoMichelin(unittest.TestCase):

    @patch('kisho_michelin.requests.get')
    def test_extract_links(self, mock_get):
        # Mock the response of requests.get
        mock_response = Mock()
        mock_response.content = '''
        <html>
            <body>
                <a href="1/1-1.htm">Link 1</a>
                <a href="2/2-2.htm">Link 2</a>
                <a href="3/3-3.htm">Link 3</a>
            </body>
        </html>
        '''
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
        mock_response.text = '''
        <html>
            <body>
                <td colspan="2"><strong>■ Book Title</strong></td>
                <td>著者</td><td>Author Name</td>
                <td>発行年月</td><td>2021年8月</td>
                <td>[総合評価]<strong>A</strong></td>
                <td>難易度</td><td>Intermediate</td>
                <td>居飛車</td>
            </body>
        </html>
        '''
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
        mock_response.text = '''
        <html>
            <table>
                <tr>
                    <td valign="top" rowspan="5" width="100"><font size="2"><img
                    src="../image/book/620/4-620-50481-5th.jpg"
                    alt="第61期将棋名人戦" border="1" width="100"
                    height="148"><br>
                    </font><a href="../image/book/620/4-620-50481-5.jpg"><font
                    size="2">zoom</font></a></td>
                    <td colspan="2"><font size="4"><strong>第61期将棋名人戦</strong></font></td>
                    <td rowspan="5" width="180" bgcolor="#E3F4FB"><font
                    size="2">[総合評価］　</font><font color="#0179FE"
                    size="6" face="Arial Black"><strong>D</strong></font><font
                    color="#0000FF" size="2"><br>
                    <br>
                    難易度：★★★☆</font><font size="2"><br>
                    図面：見開き2～3枚<br>
                    内容：（質）B（量）C<br>
                    レイアウト：B<br>
                    解説：B<br>
                    読みやすさ：B<br>
                    </font><font color="#0000FF" size="2">中級以上向き</font></td>
                    <td valign="top" rowspan="5" width="120"
                    bgcolor="#F7F7F7"><p align="center"><a href="https://www.amazon.co.jp/dp/4620504815/ref=nosim?tag=kishomichelin-22" target="_blank"><img src="../image/amazon/amazon-link.jpg" alt="この本をAmazonで見る"  align="top" border="3" width="120" height="49"></a></p>
                    </td>
                    <td>居飛車</td>
                </tr>
                <tr>
                    <td colspan="2"><font size="2">【編】　毎日新聞社</font></td>
                </tr>
                <tr>
                    <td colspan="2"><font size="2">【出版社】　毎日新聞社</font></td>
                </tr>
                <tr>
                    <td width="250"><font size="2">発行：2003年7月</font></td>
                    <td width="250"><font size="2">ISBN：4-620-50481-5</font></td>
                </tr>
                <tr>
                    <td><font size="2">定価：1,890円（5％税込）</font></td>
                    <td><font size="2">192ページ／19cm</font></td>
                </tr>
            </table>
        </html>
        '''
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
        mock_response.text = '''
        <html>
            <table border="1" cellpadding="10" cellspacing="0" width="760"
            bgcolor="#EBEBEB" bordercolordark="#FFFFFF"
            bordercolorlight="#C0C0C0">
                <tr>
                    <td valign="top" rowspan="5" width="100"><font size="2"><img
                    src="../image/book/8399/978-4-8399-2694-6th.jpg"
                    alt="二段の力" border="1" width="100" height="147"><br>
                    </font><a href="../image/book/8399/978-4-8399-2694-6.jpg"><font
                    size="2">zoom</font></a></td>
                    <td colspan="2"><font size="3">週将ブックス<br>
                    </font><font size="4"><strong>二段の力</strong></font></td>
                    <td rowspan="5" width="180" bgcolor="#E3F4FB"><font
                    size="2">[総合評価]　</font><font color="#008000"
                    size="6" face="Arial Black"><strong>C</strong></font><font
                    color="#0000FF" size="2"><br>
                    <br>
                    難易度：★★★☆</font><font size="2"><br>
                    見開き1問<br>
                    内容：（質）B（量）B<br>
                    レイアウト：A<br>
                    解答の裏透け：B<br>
                    解説：C<br>
                    </font><font color="#0000FF" size="2">上級～有段向き</font></td>
                    <td valign="top" rowspan="5" width="120" bgcolor="#F7F7F7"><p align="center"><a href="https://www.amazon.co.jp/dp/4839926948/ref=nosim?tag=kishomichelin-22" target="_blank"><img src="../image/amazon/amazon-link.jpg" alt="この本をAmazonで見る" align="top" border="3" width="120" height="49"></a></p></td>
                    <td>四間飛車</td>
                </tr>
                <tr>
                    <td colspan="2"><font size="2">【編】　週刊将棋</font></td>
                </tr>
                <tr>
                    <td colspan="2"><font size="2">【出版社】　毎日コミュニケーションズ</font></td>
                </tr>
                <tr>
                    <td width="250"><font size="2">発行：2007年12月</font></td>
                    <td width="250"><font size="2">ISBN：978-4-8399-2694-6</font></td>
                </tr>
                <tr>
                    <td><font size="2">定価：1,449円（5％税込）</font></td>
                    <td><font size="2">224ページ／19cm</font></td>
                </tr>
            </table>
        </html>
        '''
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
        mock_response.text = '''
        <html>
            <table border="1" cellpadding="10" cellspacing="0" width="760"
            bgcolor="#EBEBEB" bordercolordark="#FFFFFF"
            bordercolorlight="#C0C0C0">
                <tr>
                    <td valign="top" rowspan="5" width="100"><img
                    src="../image/book/89563/4-89563-554-6th.jpg"
                    alt="表紙：12.3KB" border="1" width="100" height="144"><br>
                    <a href="../image/book/89563/4-89563-554-6.jpg"><font size="2">zoom</font></a></td>
                    <td colspan="2"><font size="3">秘法巻之参<br>
                        </font><font size="4"><strong>大覇道伝説</strong></font>
                    </td>
                    <td rowspan="5" width="180" bgcolor="#E3F4FB">
                        <font size="2">[総合評価]　</font><font color="#008040"
                        size="6" face="Arial Black"><strong>C</strong></font><font
                        color="#0000FF" size="2"><br>
                        <br>
                        難易度：★★★★</font><font size="2"><br>
                        図面：見開き4枚<br>
                        内容：（質）B（量）A<br>
                        レイアウト：A<br>
                        解説：B<br>
                        </font><font color="#0000FF" size="2">上級～有段向き</font>
                    </td>
                    <td valign="top" rowspan="5" width="120" bgcolor="#F7F7F7">
                        <p align="center">
                            <a href="https://www.amazon.co.jp/dp/4895635546/ref=nosim?tag=kishomichelin-22" target="_blank">
                                <img src="../image/amazon/amazon-link.jpg" alt="この本をAmazonで見る" align="top" border="3" width="120" height="49">
                            </a>
                        </p>
                    </td>
                    <td>四間飛車</td>
                </tr>
                <tr>
                    <td colspan="2"><font size="2">【編　者】　週刊将棋</font></td>
                </tr>
                <tr>
                    <td colspan="2"><font size="2">【出版社】　毎日コミュニケーションズ</font></td>
                </tr>
                <tr>
                    <td width="250"><font size="2">発行：1991年9月</font></td>
                    <td width="250"><font size="2">ISBN：4-89563-554-6</font></td>
                </tr>
                <tr>
                    <td><font size="2">定価：971円</font></td>
                    <td><font size="2">215ページ／19cm</font></td>
                </tr>
            </table>
        </html>
        '''
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
        mock_response.text = '''
        <html>
            <table border="0" cellpadding="5" cellspacing="0" width="360">
                <tr>
                    <td bgcolor="#DFFFDF"><font size="6">[総合評価]</font></td>
                    <td bgcolor="#DFFFDF"><font color="#FF8000" size="6"><strong>A</strong></font></td>
                </tr>
                <tr>
                    <td><font color="#0000FF">　難易度</font></td>
                    <td><font color="#0000FF">★★★★☆</font></td>
                </tr>
                <tr>
                    <td><font color="#0000FF">　対象棋力</font></td>
                    <td><font color="#0000FF">有段向き</font></td>
                </tr>
                <tr>
                    <td>　図面</td>
                    <td>見開き4～5枚</td>
                </tr>
                <tr>
                    <td>　内容</td>
                    <td>（質）A（量）A+</td>
                </tr>
                <tr>
                    <td>　レイアウト</td>
                    <td>A</td>
                </tr>
                <tr>
                    <td>　解説</td>
                    <td>A</td>
                </tr>
                <tr>
                    <td>　読みやすさ</td>
                    <td>A</td>
                </tr>
                <tr>
                    <td>四間飛車</td>
                </tr>
            </table>
            <table border="1" cellpadding="5" cellspacing="0" width="360"
            bordercolor="#C0C0C0">
                <tr>
                    <td colspan="2" bgcolor="#FFFFE6">マイナビ将棋BOOKS<br>
                    <strong>一撃！対振り飛車へなちょこ急戦</strong></td>
                </tr>
                <tr>
                    <td>著者</td>
                    <td>Sugar</td>
                </tr>
                <tr>
                    <td>出版社</td>
                    <td>マイナビ出版</td>
                </tr>
                <tr>
                    <td>発行年月</td>
                    <td>2024年4月</td>
                </tr>
                <tr>
                    <td>ISBN</td>
                    <td>978-4-8399-8209-6</td>
                </tr>
                <tr>
                    <td>定価</td>
                    <td>1,848円（10％税込）</td>
                </tr>
                <tr>
                    <td>ページ数</td>
                    <td>318ページ</td>
                </tr>
                <tr>
                    <td>本の高さ</td>
                    <td>19cm</td>
                </tr>
            </table>
        </html>
        '''
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
        mock_response.text = '''
        <html>
            <table border="1" cellpadding="10" cellspacing="0" width="760"
            bgcolor="#EBEBEB" bordercolordark="#FFFFFF"
            bordercolorlight="#C0C0C0">
                <tr>
                    <td valign="top" rowspan="5" width="100"><img
                    src="../image/book/0276/0276-209-6016th.jpg" border="1"
                    width="100" height="158"><br>
                    <a href="../image/book/0276/0276-209-6016.jpg"><font
                    size="2">zoom</font></a></td>
                    <td colspan="2"><font size="4"><strong>入門詰将棋100題</strong></font></td>
                    <td rowspan="5" width="180" bgcolor="#E3F4FB"><font
                    size="2">[総合評価]　</font><font color="#008040"
                    size="6" face="Arial Black"><strong>C</strong></font><font
                    color="#0000FF" size="2"><br>
                    <br>
                    難易度：★</font><font size="2"><br>
                    見開き1問<br>
                    内容：（質）B（量）B<br>
                    解説：B<br>
                    </font><font color="#0000FF" size="2">初心～初級向き</font></td>
                    <td valign="top" rowspan="5" width="120" bgcolor="#F7F7F7">
                        <p align="center"><a href="https://www.amazon.co.jp/dp/B000J85EDQ/ref=nosim?tag=kishomichelin-22" target="_blank">
                        <img src="../image/amazon/amazon-link.jpg" alt="この本をAmazonで見る" align="top" border="3" width="120" height="49"></a></p>
                    </td>
                </tr>
                <tr>
                    <td colspan="2"><font size="2">【著　者】　佐瀬勇次</font></td>
                </tr>
                <tr>
                    <td colspan="2"><font size="2">【出版社】　日本文芸社</font></td>
                </tr>
                <tr>
                    <td width="250"><font size="2">発行：1980年8月</font></td>
                    <td width="250"><font size="2">0276-209-6016</font></td>
                </tr>
                <tr>
                    <td><font size="2">定価：650円</font></td>
                    <td><font size="2">210ページ／18cm</font></td>
                </tr>
                <tr>
                    <td>中飛車</td>
                </tr>
            </table>
        </html>
        '''
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

if __name__ == '__main__':
    unittest.main()
