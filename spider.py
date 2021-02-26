import re
import requests
from bs4 import BeautifulSoup


WEBSITE = 'https://korea-dpr.com/mp3/'  # Webiste to crawl
URLS = list()
PATTERN = re.compile(r'\?(C=(N|M|S|D)[;&]?O=(D|A))|\?[NMSDAnmsda]+')  # pattern to find IGNORED_HREFS
EXT_PATTERN = re.compile(r'\.[A-Za-z0-9]+$')  # pattern to find IGNORED_EXTS
IGNORED_HREFS = ['/', '../', '#', 'wget-log']  # hrefs to ignore


def is_dir(url):
    """ Returns True if given url points to a directory, otherwise returns false """
    return url.endswith('/')


def crawl(website, recursive=True, max_retries=4):
    """ Crawls the given website and yields the urls """
    # 'recursive' tells if you want to crawl through folders/directories
    # 'max_retries' is the number of retries in case request timeouts

    print(f'Crawling {website}...')

    made_sucessful_request = False
    retry_count = 0

    # Make a request and make soup
    while not made_sucessful_request:
        if retry_count >= max_retries:
            print(f'ERROR: Max number of retries ({max_retries}) reached!')
            return

        try:
            r = requests.get(website, timeout=6)
            made_sucessful_request = True

        except requests.exceptions.Timeout:
            print("ERROR: Request timed out! Retrying...")
            retry_count += 1
            continue

        except requests.exceptions.ConnectionError:
            print("ERROR: Not connected to the internet!")
            return

    soup = BeautifulSoup(r.text, 'lxml')

    # Get all the links from soup
    for link in soup.find_all('a'):
        href = link.get('href')  # Value of the href attribute of link
        # Use regex to find url patterns to ignore
        matches = re.finditer(PATTERN, href)
        for match in matches:
            # Add matches to IGNORED_URLS list
            IGNORED_HREFS.append(match.group())

        if href in IGNORED_HREFS:
            # Continue to next iteration if url is to be ignored
            continue

        elif href.startswith('/'):
            # Continue to next iteration if href starts with '/'
            # It's probably pointing to a directory, up one level in a directory tree
            continue

        url = f'{website}{href}'

        # If url points to a directory, and recursive is True
        if is_dir(url) and recursive:
            # Crawl that url
            crawl(url)
            continue

        # Otherwise
        URLS.append(url)


def get_stats():

    extensions = list()

    try:
        # Open links file to read
        file = open('links.txt', 'r')

    except FileNotFoundError:
        print("ERROR: 'links.txt' does not exist! Cannot get statistics.")
        return

    # Read urls from links file
    urls = file.read().splitlines()

    # Close the file after reading
    file.close()

    # Iterate through urls
    for url in urls:
        # Use regex to find extension pattern from url
        matches = re.finditer(EXT_PATTERN, url)
        for match in matches:
            # If extensions list does not already contain the matched extension
            if match.group() not in extensions:
                # Append matched extension to extensions list
                extensions.append(match.group().lower())
            break

    print(f'{len(urls)} total link(s)\nFound these extension(s): {extensions}')

    # Open stats file
    file = open('stats.txt', 'w')

    # Write statistics to the file
    file.write(f'URL: {WEBSITE}\n\n{len(urls)} total link(s)\nFound these extension(s): {extensions}\n')

    # Get file counts
    # Iterate through extensions
    for ext in extensions:
        # Set file count initially to 0
        file_count = 0
        # Iterate through urls
        for url in urls:
            # If extension is in the url
            for match in re.finditer(f'{ext}$', url):
                # Increment file count
                file_count += 1

        print(f'{ext}: {file_count} file(s)')

        # Write file counts to the file
        file.write(f'{ext}: {file_count} file(s)\n')

    # Close the file after reading
    file.close()


def main():
    # Crawl the wesbite
    crawl(WEBSITE)

    # Write urls to a text file
    with open('links.txt', 'a') as file:
        for url in URLS:
            file.write(f'{url.lower()}\n')

    # Get the statistics
    get_stats()


if __name__ == '__main__':
    main()
