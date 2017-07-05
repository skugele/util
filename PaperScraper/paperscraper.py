import re
import urllib
import bs4 as bslib
import urlparse
import os

HTTP_SUCCESS = 200

DEBUG = 1


class PaperScraper(object):
    @staticmethod
    def visit(url):
        return urllib.urlopen(url)

    @staticmethod
    def parse(response):
        htmlbytes = response.read()

        parsed_response = ParsedResponse()

        parser = bslib.BeautifulSoup(htmlbytes, 'html.parser')

        for tag in parser.find_all('p'):

            try:

                if Paper.is_paper(tag):
                    parsed_response.papers.append(Paper.parse_tag(tag, url=response.geturl()))

            except ValueError as e:
                print(e)

        return parsed_response

    @staticmethod
    def write(path, paper):
        out_file = paper.link.split('/')[-1]
        out_path = '/'.join([path, paper.year])

        if not os.path.exists(out_path):
            os.mkdir(out_path)

        resp = PaperScraper.visit(paper.link)
        if resp.getcode() == HTTP_SUCCESS:
            with open('/'.join([out_path, out_file]), 'wb') as fd:
                fd.write(resp.read())
        else:
            print("Failed to download paper: {} [status={}]".format(
                paper.link, resp.getcode()))


class ParsedResponse(object):
    def __init__(self):
        self.papers = []


class Paper(object):
    FILE_TYPES = ('doc', 'pdf')

    def __init__(self):
        self.title = ''
        self.link = ''
        self.year = ''
        self.authors = []

    @staticmethod
    def parse_tag(tag, url=None):
        new_paper = Paper()

        text = re.sub('\s+', ' ', tag.get_text())

        match = re.search('\(?(?:((?:19|20)\d{2})\s*(?:in press)?)\)?\.?\s+([^.?,]+)', text)
        if match:
            new_paper.year = match.group(1)
        else:
            raise ValueError("Invalid Tag Format: {}".format(text))

        new_paper.link = urlparse.urljoin(base=url, url=tag.a.get('href'))

        return new_paper

    @staticmethod
    def is_paper(tag):
        accepted = False

        children = tag.children
        for c in children:
            if c.name == 'a':
                if Paper.is_paper_link(c.get('href')):
                    accepted = True

        return accepted

    @staticmethod
    def is_paper_link(link):
        accepted = False

        if any(t in link.lower() for t in Paper.FILE_TYPES):
            accepted = True

        return accepted

    def __str__(self):
        return '({}) [{}]'.format(self.year, self.link)


if __name__ == '__main__':
    response = PaperScraper.visit(url='http://ccrg.cs.memphis.edu/papers.html')
    if response.getcode() == HTTP_SUCCESS:

        parsed_response = PaperScraper.parse(response)
        for paper in parsed_response.papers:
            PaperScraper.write(path='/home/vagrant/Papers/ccrg', paper=paper)

    else:
        print('Received unexpected status from remote host: {}'.format(response.getcode()))
