import threading
import queue
import requests
import time

# Create a queue for proxies and valid proxies
q = queue.Queue()
valid_proxies = []

# Read proxies from the file
with open("data.txt", "r") as f:
    proxies = f.read().split("\n")
    for p in proxies:
        q.put(p)

# Function to check the validity of proxies
def check_proxies():
    global q
    while True:
        proxy = q.get()
        if proxy is None:
            break  # No more items in the queue, exit the thread
        try:
            res = requests.get(
                "http://ipinfo.io/json",
                proxies={"http": proxy, "https": proxy},
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            if res.status_code == 200:
                valid_proxies.append(proxy)
                print(f"Valid proxy: {proxy}")
        except Exception as e:
            continue

# Create and start threads for proxy validation
threads = []
for _ in range(10):
    thread = threading.Thread(target=check_proxies)
    thread.start()
    threads.append(thread)

# Wait for all proxy validation threads to finish
for thread in threads:
    q.put(None)  # Signal threads to exit
for thread in threads:
    thread.join()

# Print valid proxies
print("Valid proxies:")
for proxy in valid_proxies:
    print(proxy)

# Use the valid proxies to make requests to specific websites
sites_to_check = [
    "http://books.toscrape.com/catalogue/category/books/fiction_10/index.html",
    "http://books.toscrape.com/catalogue/category/books/womens-fiction_9/index.html",
    "http://books.toscrape.com/catalogue/category/books/science-fiction_16/index.html"
]

for site in sites_to_check:
    for proxy in valid_proxies:
        try:
            print(f"Using the proxy: {proxy}")
            res = requests.get(
                site,
                proxies={"http": proxy, "https": proxy},
                timeout=10
            )

            if res.status_code == 200:
                print(f"Proxy {proxy} succeeded for {site}")
                break  # Move to the next site
            else:
                print(f"Proxy {proxy} failed for {site}, Status Code: {res.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Proxy {proxy} failed for {site}: {str(e)}")
        except Exception as e:
            print(f"An error occurred for {site}: {str(e)}")
