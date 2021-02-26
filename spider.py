import re
import requests
from bs4 import BeautifulSoup


PATTERN = re.compile(r'\?(C=(N|M|S|D)[;&]?O=(D|A))|\?[NMSDAnmsda]+')  # pattern to find IGNORED_HREFS
EXT_PATTERN = re.compile(r'\.[A-Za-z0-9]+$')  # pattern to find IGNORED_EXTS
IGNORED_HREFS = ['/', '../', '#', 'wget-log']  # hrefs to ignore


def is_dir(url):
    """ Returns True if given url points to a directory, otherwise returns false """
    return url.endswith('/')


def write_url(url):
    """ Appends links to a text file """
    with open('links.txt', 'a') as file:
        file.write(url.lower() + "\n")


def write_stats(stat):
    """ Appends statistics to a text file """
    with open('stats.txt', 'a') as file:
        file.write(stat + "\n")


def crawl(website, recursive=True, max_retries=3):
    """ Crawls the given website. 'recursive' tells if you want to crawl through folders/directories """
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

    soup = BeautifulSoup(r.text, 'html.parser')

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

        # Sometimes hrefs start from '/'. e.g. "/books/", "/songs/" etc.
        # If that's the case, ignore the first '/' in href
        url = website + (href[1:] if href.startswith('/') else href)

        # If url points to a directory, and recursive is True
        if is_dir(url) and recursive:
            # Crawl that url
            crawl(url)
            continue

        # Otherwise
        write_url(url)  # Write that url to a file


def count_extensions(extensions):
    """ Prints the count of files belonging to an extension """

    # Iterate through extensions list
    for ext in extensions:
        ext_count = 0  # Extension Count

        # Open links file to read
        with open('links.txt', 'r') as links:
            # Iterate through the lines
            for line in links:
                # Use regex to find extension instances on line
                matches = re.findall(f'.{ext}$', line)
                # Count extensions
                ext_count += len(matches)

        print(f'{ext}: {ext_count} file(s)')
        write_stats(f'{ext}: {ext_count} file(s)')


def getStats():
    """ Shows statistics related to OD """

    # Make an empty extensions list
    extensions = list()

    try:
        # Open links file to read
        file = open('links.txt', 'r')

    except FileNotFoundError:
        print("ERROR: 'links.txt' does not exist! Cannot write statistics.")
        return

    links = file.readlines()
    # Iterate through each line
    for line in links:
        # Use regex to find extension patterns in line
        matches = re.finditer(EXT_PATTERN, line)
        for match in matches:
            # Add matches to extensions list
            extensions.append(match.group().lower())  # Used lower() for string comparison

        # Convert extensions list to a set
        # to filter out the duplicate extensions from the list
        extensions_set = set(extensions)

        # Convert the set back to list (without duplicates)
        extensions = list(extensions_set)

    # Print the results
    print(f'{len(links)} total link(s)')
    print(f'Found these extension(s): {extensions}')

    # Write the results to stats file
    write_stats(f'{len(links)} total link(s)\nFound these extension(s): {extensions}')

    file.close()

    # Count the no. of files belonging to each extension
    count_extensions(extensions)


def main():
    # Webiste to crawl
    website = 'https://korea-dpr.com/mp3/'
    # website = 'http://34.105.17.91:8000/'

    # Crawl the wesbite
    crawl(website)

    # Write the website URL to stats file
    write_stats(f'URL: {website}\n')

    # get the stats and print them
    getStats()


if __name__ == '__main__':
    main()
