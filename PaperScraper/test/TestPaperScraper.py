import unittest
import paperscraper as ps
import bs4


class TestPaperScraper(unittest.TestCase):
    def test_retrieve_page(self):
        response = ps.PaperScraper.visit(url='http://ccrg.cs.memphis.edu/papers.html')
        self.assertEqual(response.getcode(), 200)

        parsed_response = ps.PaperScraper.parse(response)
        self.assertTrue(len(parsed_response.papers) > 0)

    def test_write(self):
        response = ps.PaperScraper.visit(url='http://ccrg.cs.memphis.edu/papers.html')
        parsed_response = ps.PaperScraper.parse(response)
        paper = parsed_response.papers[0]

        ps.PaperScraper.write('/home/vagrant/Papers/ccrg', paper)


class TestPaper(unittest.TestCase):
    def test_is_paper(self):
        paper1_html = """
        <html>
        <body>
           <p>Franklin, S., Madl, T., Strain, S., Faghihi, U., Dong, D.,
           Kugele, S., Snaider, J., Agrawal, P., Chen, S. (2016). A LIDA
           cognitive model tutorial. Biologically Inspired Cognitive Architectures,
           105-130. doi: 10.1016/j.bica.2016.04.003
           (View: 
               <a href="assets/papers/2016/BICA-D-16-00011R1.pdf"> PDF</a>
               )
           </p>
        </body>
        </html>
        """

        not_a_paper_html = """
        <html>
        <body>
           <p>This is most definitely not a paper!</p>
        </body>
        </html>
        """

        bs = bs4.BeautifulSoup(paper1_html, 'html.parser')
        self.assertTrue(ps.Paper.is_paper(bs.body.p))

        bs = bs4.BeautifulSoup(not_a_paper_html, 'html.parser')
        self.assertFalse(ps.Paper.is_paper(bs.body.p))

    def test_is_paper_link(self):
        self.assertTrue(ps.Paper.is_paper_link("../paper.doc"))
        self.assertTrue(ps.Paper.is_paper_link("../paper.DOC"))
        self.assertTrue(ps.Paper.is_paper_link("../paper.pdf"))
        self.assertTrue(ps.Paper.is_paper_link("../paper.PDF"))

        self.assertFalse(ps.Paper.is_paper_link("../paper.html"))
        self.assertFalse(ps.Paper.is_paper_link("../paper.HTML"))
        self.assertFalse(ps.Paper.is_paper_link("not/a/paper/link"))

    def test_parse_paper_tag(self):
        paper_html = """
        <html>
        <body>
           <p>Franklin, S., Madl, T., Strain, S., Faghihi, U., Dong, D.,
           Kugele, S., Snaider, J., Agrawal, P., Chen, S. (2016). A LIDA
           cognitive model tutorial. Biologically Inspired Cognitive Architectures,
           105-130. doi: 10.1016/j.bica.2016.04.003
           (View: 
               <a href="assets/papers/2016/BICA-D-16-00011R1.pdf"> PDF</a>
               )
           </p>
        </body>
        </html>
        """

        paper_with_absolute_link_html = """
        <html>
        <body>
           <p>Franklin, S., Madl, T., Strain, S., Faghihi, U., Dong, D.,
           Kugele, S., Snaider, J., Agrawal, P., Chen, S. (2016). A LIDA
           cognitive model tutorial. Biologically Inspired Cognitive Architectures,
           105-130. doi: 10.1016/j.bica.2016.04.003
           (View: 
               <a href="http://another_site/assets/papers/2010/paper.doc"> doc </a>
               )
           </p>
        </body>
        </html>
        """

        bs = bs4.BeautifulSoup(paper_html, 'html.parser')

        p = ps.Paper.parse_tag(bs.body.p)
        self.assertEqual(p.year, '2016')
        self.assertEqual(p.link, 'assets/papers/2016/BICA-D-16-00011R1.pdf')

        bs = bs4.BeautifulSoup(paper_with_absolute_link_html, 'html.parser')
        p = ps.Paper.parse_tag(bs.body.p, url="http://ccrg.cs.memphis.edu/papers.html")
        self.assertEqual(p.year, '2016')
        self.assertEqual(p.link, 'http://another_site/assets/papers/2010/paper.doc')
