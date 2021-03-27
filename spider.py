from indexer import Indexer
import os

def main():
    url_files_input = ["urls.txt"]
    url_file_output = "all_urls.txt"

    idx = Indexer()
    
    scan_queue = [
        # URLs go here! (entries are separated by ",")
        # 'http://s28.bitdl.ir/Video/',
        # 'http://128.199.129.79:666/',
        # 'https://korea-dpr.com/mp3/',
        # 'http://46.4.132.219:999/',
        'https://mirror.futureweb.be/manjaro/arm-stable/'
    ]

    # If sny of the input URL files exist, add it to the list as well
    for url_file_input in url_files_input:
        if url_file_input in os.listdir():
            with open(url_file_input, 'r') as f:
                for line in f.readlines():
                    # Strips whitespace in case there is extra at the end of the line
                    # Splits by space in case there are multiple words or a comment after that (meaning 1 URL per line and it must be at the beginning of the line)
                    # If the first character of the first word of the line is '#', skip the line
                    split = line.strip().split(' ')
                    if split[0][0] != "#":
                        scan_queue.append(split[0])
    
    urls = idx.scan(scan_queue)

    idx.save(url_file_output, urls)

if __name__ == '__main__':
    main()
