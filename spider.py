from indexer import Indexer


def main():
    idx = Indexer()

    scan_queue = [
        # 'http://s28.bitdl.ir/Video/',
        # 'http://128.199.129.79:666/',
        # 'https://korea-dpr.com/mp3/',
        # 'http://46.4.132.219:999/',
        'https://mirror.futureweb.be/manjaro/arm-stable/',
    ]

    urls = idx.scan(scan_queue)

    idx.save('urls.txt', urls)


if __name__ == '__main__':
    main()
