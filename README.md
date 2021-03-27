# spider

# Table of Contents
- [What is this?](#what-is-this)
- [Installation](#installation)
    - [Adding URLS](#adding-urls)
- [Contributions](#Contributions)

# What Is This?
An OD crawler that crawls through open directories and indexes the urls.

# Installation
To get this repository, download it from `Code > Download Zip` or clone it using `git clone https://github.com/pyDiablo/spider` or using wget (`wget https://github.com/pyDiablo/spider`).

After that is done, change to the `spider/` directory and run `pip install requirements.txt` to make sure you have all the required Python libraries.

## Adding URLs
In the `spider.py` file, add the URLs you want scanned to the `scan_queue` array, or add them in a file called `urls.txt` in the same folder.

# Running the Program
To run this program, open a Terminal in the directory these files are stored, then run `python3 spider.py`.

# Contributions
A huge thank you to:

- [u/Gongui](https://www.reddit.com/user/Gongui) on **Reddit** (for adding threads, queues and structuring the code with OOP)
