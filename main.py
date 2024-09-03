import warnings
import coinmarketcap as marketcap
import cointelegraph as telegraph

OUTPUT_DIR = "articles.csv"

if __name__ == "__main__":
    warnings.filterwarnings("ignore", message="Unverified HTTPS request")
    telegraph.crawl(OUTPUT_DIR)
    marketcap.crawl(OUTPUT_DIR,5)