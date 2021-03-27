from indexer import Indexer
import os

def main():
    url_file_input = "urls.txt"
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

    # If the input URLs file exists, add it to the list as well
    if url_file_input in os.listdir():
        with open(url_file_input, 'r') as f:
            for line in f.readlines():
                scan_queue.append(line)
    
    urls = idx.scan(scan_queue)

    idx.save(url_file_output, urls)

if __name__ == '__main__':
    main()
