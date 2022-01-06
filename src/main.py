
from androZoOpenCrawler import AndroZooOpenCrawler


CONFIG_FILE="config.json"

if __name__ == '__main__':
    x = AndroZooOpenCrawler(CONFIG_FILE)
    x.process_input_file()