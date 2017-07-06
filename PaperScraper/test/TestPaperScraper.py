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

        paper2_html = """
        <html>
        <body>
            <p>Franklin, Stan, Sidney D'Mello, Bernard J Baars, and Uma  Ramamurthy. (2009). Evolutionary pressures for perceptual stability and self as guides to machine consciousness. International Journal of  Machine Consciousness.<br>
            (View: 
            <a href="abstracts/Evolutionary-Pressures-2009.html" onClick="return popup(this, 'notes')">Abstract</a> 
                or 
            <a href="assets/papers/2009/Evolutionary-Pressures-2009.pdf">PDF</a>
            )
            </p>
        </body>
        </html>
        """

        not_a_paper_html = """
        <html>
        <body>
			<p>
            Franklin, S. (2009). Into the Future. In R. Ruggies (Ed.), Knowledge Management Tools (pp. 287-295). 
            Boston: Butterworth-Heinemann. (Reprinted from Artificial Minds)
            </p>
        </body>
        </html>
        """

        bs = bs4.BeautifulSoup(paper1_html, 'html.parser')
        self.assertTrue(ps.Paper.is_paper(bs.body.p))

        bs = bs4.BeautifulSoup(paper2_html, 'html.parser')
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

        paper_with_multiple_links_html = """
         <html>
         <body>
            <p>Sun, Ron and Stan Franklin. (2007). Computational models of consciousness: 
              A taxonomy and some examples. In Cambridge handbook of consciousness, 
              ed. P D Zelazo and Morris Moscovitch:151&shy;174.<br>
              New York: Cambridge University Press.<br>
            (View:<a href="abstracts/0521857430c07_p151-174 (Ch 7 Sun Franklin).html" 
   onClick="return popup(this, 'notes')">Abstract</a> 
              or <a href="assets/papers/0521857430c07_p151-174 (Ch 7 Sun Franklin).pdf">PDF</a>)
            </p>
         </body>
         </html>
         """

        paper_with_multiple_links_html_2 = """
        <html>
        <body>
            <p>Franklin, Stan, Sidney D'Mello, Bernard J Baars, and Uma  Ramamurthy. (2009). Evolutionary pressures for perceptual stability and self as guides to machine consciousness. International Journal of  Machine Consciousness.<br>
            (View: 
            <a href="abstracts/Evolutionary-Pressures-2009.html" onClick="return popup(this, 'notes')">Abstract</a> 
                or 
            <a href="assets/papers/2009/Evolutionary-Pressures-2009.pdf">PDF</a>
            )
            </p>
        </body>
        </html>
        """

        bs = bs4.BeautifulSoup(paper_html, 'html.parser')
        p = ps.Paper.parse_tag(bs.body.p)
        self.assertEqual(p.year, '2016')
        self.assertIn('assets/papers/2016/BICA-D-16-00011R1.pdf', p.links)

        bs = bs4.BeautifulSoup(paper_html, 'html.parser')
        p = ps.Paper.parse_tag(bs.body.p, url="http://ccrg.cs.memphis.edu/papers.html")
        self.assertEqual(p.year, '2016')
        self.assertIn('http://ccrg.cs.memphis.edu/assets/papers/2016/BICA-D-16-00011R1.pdf', p.links)

        bs = bs4.BeautifulSoup(paper_with_absolute_link_html, 'html.parser')
        p = ps.Paper.parse_tag(bs.body.p, url="http://ccrg.cs.memphis.edu/papers.html")
        self.assertEqual(p.year, '2016')
        self.assertIn('http://another_site/assets/papers/2010/paper.doc', p.links)

        bs = bs4.BeautifulSoup(paper_with_multiple_links_html, 'html.parser')
        p = ps.Paper.parse_tag(bs.body.p, url="http://ccrg.cs.memphis.edu/papers.html")
        self.assertEqual(p.year, '2007')
        self.assertIn('http://ccrg.cs.memphis.edu/assets/papers/0521857430c07_p151-174 (Ch 7 Sun Franklin).pdf',
                      p.links)

        bs = bs4.BeautifulSoup(paper_with_multiple_links_html_2, 'html.parser')
        p = ps.Paper.parse_tag(bs.body.p, url="http://ccrg.cs.memphis.edu/papers.html")
        self.assertEqual(p.year, '2009')
        self.assertIn('http://ccrg.cs.memphis.edu/assets/papers/2009/Evolutionary-Pressures-2009.pdf', p.links)
