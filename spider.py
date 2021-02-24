import re
import requests
from bs4 import BeautifulSoup


PATTERN = re.compile(r'\?(C=(N|M|S|D)[;&]?O=(D|A))|\?[NMSDAnmsda]+')  # pattern to find IGNORED_HREFS
EXT_PATTERN = re.compile(r'\.[A-Za-z0-9]+$')  # pattern to find IGNORED_EXTS
IGNORED_HREFS = ['/', '../', '#', 'wget-log']  # hrefs to ignore


def is_dir(url):
    """ Returns True if given url belongs to a directory, otherwise returns false """
    # could be return url[-1] == '/' as well
    return url.endswith('/')


def write_link(url):
    """ Appends links to a text file """
    with open('links.txt', 'a') as file:
        file.write(url + "\n")


def write_stats(stat):
    """ Appends statistics to a text file """
    with open('stats.txt', 'a') as file:
        file.write(stat + "\n")


def crawl(website, recursive=True, timeout_length_seconds=6, max_number_of_timeouts=5):
    """ Crawls the given website. 'recursive' tells if you want to crawl through folders/directories """
    print(f'Crawling {website}...')

    # Make a request and make soup
    made_sucessful_request = False
    timeout_counter = 0
    while not made_sucessful_request:
        if timeout_counter >= max_number_of_timeouts:
            print(f'ERROR: Max number ({max_number_of_timeouts}) of timeouts reached')
            return

        try:
            r = requests.get(website, timeout=timeout_length_seconds)
            made_sucessful_request = True

        except requests.exceptions.Timeout:
            timeout_counter += 1
            continue

        except requests.exceptions.ConnectionError:
            print("ERROR: Request timed out!\nRetrying in 5 seconds...")
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

        # Otherwise, do this:

        # Sometimes urls start from '/'. e.g. "/books/", "/songs/" etc.
        # If that's the case, ignore the first element of url i.e. '/'
        url = website + (href[1:] if href.startswith('/') else href)

        if is_dir(url) and recursive:
            # If url points to a directory, and recursive is True
            # Crawl that url
            crawl(
                url,
                recursive=recursive,
                timeout_length_seconds=timeout_length_seconds,
                max_number_of_timeouts=max_number_of_timeouts
            )
            continue

        # If url points to a file
        write_link(url)  # Write that url to a file


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

        print(f'{ext}: {ext_count} files')
        write_stats(f'{ext}: {ext_count} files')


def getStats():
    """ Shows statistics related to OD """

    # Make an empty extensions list
    extensions = list()

    # Open links file to read
    with open('links.txt', 'r') as f:
        links = f.readlines()
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
    print(f'{len(links)} total links')
    print(f'Found these extensions: {extensions}')

    # Write the results to stats file
    write_stats(f'{len(links)} total links\nFound these extensions: {extensions}')

    # Count the no. of files belonging to each extension
    count_extensions(extensions)


def main():
    # Webiste to crawl
    website = 'https://korea-dpr.com/mp3/'

    # Crawl the wesbite
    crawl(website)

    # Write the website URL to stats file
    write_stats(f'URL: {website}\n')

    # get the stats and print them
    getStats()


if __name__ == '__main__':
    main()
