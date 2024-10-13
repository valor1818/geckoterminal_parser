import requests
import time
import json
import configparser
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("price_tracker.log"),
            logging.StreamHandler()
        ]
    )

def parse_price(network, address):
    api_url = f'https://api.geckoterminal.com/api/v2/simple/networks/{network}/token_price/{address}'
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        datajson = response.json()
        price = float(datajson['data']['attributes']['token_prices'][address])
        return price
    except requests.RequestException as e:
        logging.error(f"Error fetching price: {e}")
        return None
    except (KeyError, ValueError) as e:
        logging.error(f"Error parsing response: {e}")
        return None

def track_price(network, address, interval):
    setup_logging()
    logging.info(f"Starting price tracking for token on network '{network}' with address '{address}'")

    price = parse_price(network, address)
    if price is None:
        logging.error("Failed to fetch the initial price. Exiting.")
        return

    while True:
        old_price = price
        price = parse_price(network, address)
        
        if price is None:
            logging.warning("Retrying to fetch the price...")
            time.sleep(interval)
            continue

        if price != old_price:
            price_change = price - old_price
            price_change_percent = (price_change / old_price) * 100 if old_price != 0 else 0

            logging.info(f"Current Price: {price:.10f} | Change: {price_change:.10f} | Percent Change: {price_change_percent:.2f}%")

        time.sleep(interval)

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    network = config.get('SETTINGS', 'Network')
    address = config.get('SETTINGS', 'TokenAddress')
    interval = config.getint('SETTINGS', 'UpdateInterval', fallback=5)

    track_price(network, address, interval)
