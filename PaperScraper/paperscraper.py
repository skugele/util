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
        out_path = '/'.join([path, paper.year])

        if not os.path.exists(out_path):
            os.mkdir(out_path)

        for link in paper.links:
            out_file = '/'.join([out_path, link.split('/')[-1]])

            print('Downloading paper from link ({})'.format(link))
            resp = PaperScraper.visit(link)
            if resp.getcode() == HTTP_SUCCESS:
                with open(out_file, 'wb') as fd:
                    fd.write(resp.read())
            else:
                print('Failed to download paper: {} [status={}]'.format(link, resp.getcode()))


class ParsedResponse(object):
    def __init__(self):
        self.papers = []


class Paper(object):
    FILE_TYPES = ('doc', 'pdf')

    def __init__(self):
        self.title = ''
        self.links = []
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

        for link in tag.find_all('a'):
            if Paper.is_paper_link(link.get('href')):
                new_paper.links.append(urlparse.urljoin(base=url, url=link.get('href')))

        return new_paper

    @staticmethod
    def is_paper(tag):
        accepted = False

        for candidate in tag.find_all('a'):
            if Paper.is_paper_link(candidate.get('href')):
                accepted = True

        return accepted

    @staticmethod
    def is_paper_link(link):
        accepted = False

        if link:
            if any(t in link.lower() for t in Paper.FILE_TYPES):
                accepted = True

        return accepted

    def __str__(self):
        return '({}) [{}]'.format(self.year, self.links)


if __name__ == '__main__':
    response = PaperScraper.visit(url='http://ccrg.cs.memphis.edu/papers.html')
    if response.getcode() == HTTP_SUCCESS:

        parsed_response = PaperScraper.parse(response)
        for paper in parsed_response.papers:
            PaperScraper.write(path='/home/vagrant/Papers/ccrg', paper=paper)

    else:
        print('Received unexpected status from remote host: {}'.format(response.getcode()))
