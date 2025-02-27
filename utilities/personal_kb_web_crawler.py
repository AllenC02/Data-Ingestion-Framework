import scrapy
import scrapy.crawler as crawler
from scrapy.utils.log import configure_logging
from multiprocessing import Process, Queue
from twisted.internet import reactor
import logging
import os

class WebsiteSpider(scrapy.Spider):
    name = 'website_spider'

    def __init__(self, urls, source_metadata, output_path, *args, **kwargs):
        super(WebsiteSpider, self).__init__(*args, **kwargs)
        self.start_urls = urls
        self.source_metadata = source_metadata

        # Debugging to ensure the settings are being applied
        logging.warning(f"Setting custom FEEDS path to {output_path}")

        self.custom_settings = {
            'FEEDS': {
                output_path: {
                    'format': 'json',
                    'encoding': 'utf8',
                    'store_empty': False,
                    'fields': None,
                    'indent': 4,
                },
            }
        }

    def parse(self, response):
        content = ' '.join([p.get() for p in response.css('p::text')])
        yield {
            'content': content,
            'metadata': {
                'source': self.source_metadata,
                'identifier': response.url
            }
        }

def run_spider_process(urls, q, source_metadata, output_path):
    try:
        settings = {
            'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
            'FEEDS': {
                output_path: {
                    'format': 'json',
                    'encoding': 'utf8',
                    'store_empty': False,
                    'fields': None,
                    'indent': 4,
                },
            }
        }

        # Debugging to ensure the settings are being applied
        logging.warning(f"Applying FEEDS path to {output_path}")

        runner = crawler.CrawlerRunner(settings)
        deferred = runner.crawl(WebsiteSpider, urls=urls, source_metadata=source_metadata, output_path=output_path)
        deferred.addBoth(lambda _: reactor.stop())
        reactor.run()
        q.put(None)
    except Exception as e:
        q.put(e)

def run_spider(urls, source_metadata, output_path):
    # Ensure the output file is wiped before running the spider
    if os.path.exists(output_path):
        open(output_path, 'w').close()

    # Debugging to ensure the directory exists
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        logging.warning(f"Creating directory {output_dir}")
        os.makedirs(output_dir)
    else:
        logging.warning(f"Directory {output_dir} already exists")

    q = Queue()
    p = Process(target=run_spider_process, args=(urls, q, source_metadata, output_path))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result

# Main script execution

# Configure logging once at the beginning
# configure_logging() -> THIS DIDN'T REMOVE ALL WARNINGS
configure_logging(install_root_handler=False)
logging.basicConfig(
    format='%(levelname)s: %(message)s',
    level=logging.WARNING
)

if __name__ == "__main__":
    source_metadata = "Link"
    urls = ["https://python.langchain.com/v0.1/docs/modules/model_io/prompts/quick_start/",
    "https://www.theverge.com/2024/5/30/24167986/perplexity-ai-research-pages-school-report",
    "https://a16z.com/owning-the-workflow-in-b2b-ai-apps/"]
    output_path = os.path.join("user_kb", "extracted_links.json")

    # Debugging to confirm the final output path
    logging.warning(f"Final output path: {output_path}")

    run_spider(urls, source_metadata, output_path)
