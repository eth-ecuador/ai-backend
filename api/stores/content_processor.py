from bs4 import BeautifulSoup
import re


class ContentProcessor:
    def __init__(self):
        pass

    def process_page(self, url, html_content, max_content_length=10000):
        soup = BeautifulSoup(html_content, 'html.parser')

        # Content segmentation
        content_blocks = []
        # for element in soup.find_all(['div', 'section', 'article']):
        element = soup.find('main')
        if element.find('article'):
            type = 'text'
            text = self._clean_text(element.find('article'))
            if len(text) > max_content_length:
                text = text[:max_content_length] + " [TRUNCATED]"
            metadata = {
                'url': url,
                'type': type,
                # Convert list to string
                'breadcrumbs': " | ".join(self._get_breadcrumbs(soup)),
                # Flatten headings
                'headings': "; ".join([f"{h['level']}: {h['text']}" for h in self._get_headings(soup)]),
                'last_updated': self._get_last_modified(soup) or "unknown",
                # Flatten links
                'related_links': "; ".join([f"{link['text']}: {link['url']}" for link in self._get_related_links(soup)]),
                'content': text
            }
            content_blocks.append({
                'type': type,
                'content': text,
                'embedding': None,
                'metadata': metadata
            })

        # for element in soup.find_all(['main']):
        if element.find('pre') or element.find('code'):
            for code_block in element.find_all(['pre', 'code']):
                type = 'code'
                text = self._clean_code(code_block)
                metadata = {
                    'url': url,
                    'type': type,
                    # Convert list to string
                    'breadcrumbs': " | ".join(self._get_breadcrumbs(soup)),
                    # Flatten headings
                    'headings': "; ".join([f"{h['level']}: {h['text']}" for h in self._get_headings(soup)]),
                    'last_updated': self._get_last_modified(soup) or "unknown",
                    # Flatten links
                    'related_links': "; ".join([f"{link['text']}: {link['url']}" for link in self._get_related_links(soup)]),
                    'content': text
                }
                content_blocks.append({
                    'type': type,
                    'content': text,
                    'embedding': None,
                    'metadata': metadata
                })

        return content_blocks

    def _get_breadcrumbs(self, soup):
        """
        Extract breadcrumbs from the page (if available).
        Breadcrumbs are typically found in a nav or ol/ul element with class 'breadcrumb'.
        """
        breadcrumb = soup.find('nav', class_='breadcrumb') or soup.find(
            'ol', class_='breadcrumb') or soup.find('ul', class_='breadcrumb')
        if breadcrumb:
            return [item.text.strip() for item in breadcrumb.find_all('li')]
        return []

    def _get_headings(self, soup):
        """
        Extract all headings (h1-h6) from the page.
        """
        return [{'level': int(h.name[1]), 'text': h.text.strip()}
                for h in soup.find_all(re.compile('^h[1-6]$'))]

    def _get_last_modified(self, soup):
        """
        Extract the last modified date (if available).
        """
        last_modified = soup.find('time') or soup.find(
            'span', class_='last-modified')
        return last_modified['datetime'] if last_modified and last_modified.has_attr('datetime') else None

    def _get_related_links(self, soup):
        """
        Extract related links (if available).
        """
        related_links = soup.find(
            'div', class_='related-links') or soup.find('aside', class_='related')
        if related_links:
            return [{'text': a.text.strip(), 'url': a['href']}
                    for a in related_links.find_all('a', href=True)]
        return []

    def _clean_code(self, element):
        """
        Clean and extract code blocks.
        """
        # code = element.text
        code = element.text
        return re.sub(r'\s+', ' ', code).strip()

    def _clean_text(self, element):
        """
        Clean and extract non-code text.
        """
        # for tag in ['h2', 'h3', 'h4', 'p']:
        #     for match in element.find_all(tag):
        #         match.decompose()
        text = element.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)
        return text
