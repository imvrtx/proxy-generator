import time
import requests
import threading
import re
import os
import json

URL = "http://httpbin.org/ip"
HTTP_PROXY_FILENAME = "http.txt"
SUCCESS_COUNT = -1
PROXY_LIST_URLS = [
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=https&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/themiralay/Proxy-List-World/master/data.txt",
    "https://raw.githubusercontent.com/casals-ar/proxy-list/main/http",
    "https://raw.githubusercontent.com/casals-ar/proxy-list/main/https",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/http/global/http_checked.txt",
    "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt"
]

def get_proxies(url, timeout=5):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text.splitlines()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

def scrape_website(url, timeout=5):
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    proxies = get_proxies(url, timeout=timeout)
    with threading.Lock():
        all_proxies.extend(proxies)
    print(f"Website scraped: {url}")
    if config.get("clearcmd", True):
        os.system('cls' if os.name == 'nt' else 'clear')


def main(timeout=5):
    global all_proxies
    all_proxies = []
    threads = [threading.Thread(target=scrape_website, args=(url, timeout)) for url in PROXY_LIST_URLS]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    filename = HTTP_PROXY_FILENAME
    if not os.path.exists(filename):
        print(f"The file {filename} does not exist. Creating it.")
        open(filename, 'w').close()
    with open(filename, "w", encoding="utf-8") as file:
        file.writelines(proxy + "\n" for proxy in all_proxies)
    print(f"Total proxies saved: {len(all_proxies)}")

def remove_invalid_proxies(filename):
    if not os.path.exists(filename):
        print(f"The file {filename} does not exist. Creating it.")
        open(filename, 'w').close()
    with open(filename, "r", encoding="utf-8") as file:
        proxies = file.read().splitlines()
    valid_proxies = [proxy for proxy in proxies if re.match(r"\d+\.\d+\.\d+\.\d+:\d+", proxy)]
    with open(filename, "w", encoding="utf-8") as file:
        file.writelines(proxy + "\n" for proxy in valid_proxies)
    print(f"Total valid proxies: {len(valid_proxies)}")

def update_title(mode):
    if mode == "setup":
        title = f"title Proxy Scraper / github.com/vortexsys / Setup"
        os.system(title)
    elif mode == "start":
        global SUCCESS_COUNT
        SUCCESS_COUNT += 1
        title = f"title Proxy Scraper / github.com/vortexsys / {SUCCESS_COUNT} working proxies"
        os.system(title)

def check_proxy(proxy, working_proxies, unchecked_proxies):
    url = URL
    try:
        response = requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=10)
        response.raise_for_status()
        print(f"Proxy {proxy} is working fine")
        working_proxies.add(proxy)
        with open("http_check.txt", "a", encoding="utf-8") as file:
            file.write(proxy + "\n")
            update_title("start")
            unchecked_proxies.discard(proxy)
        with open("proxies.txt", "a", encoding="utf-8") as file:
            file.write(proxy + "\n")
            unchecked_proxies.discard(proxy)
    except requests.exceptions.RequestException as e:
        pass

def clear_file(filename):
    with open(filename, "w"):
        pass

def remove_duplicates(filename):
    with open(filename, "r", encoding="utf-8") as file:
        lines = file.read().splitlines()

    unique_lines = set(lines)
    lines_to_remove = set(line for line in unique_lines if lines.count(line) > 2)

    with open(filename, "w", encoding="utf-8") as file:
        file.writelines(line + "\n" for line in lines if line not in lines_to_remove)

def check_proxies_from_file(filename):
    if not os.path.exists(filename):
        print(f"The file {filename} does not exist. Creating it.")
        open(filename, 'w').close()
    with open(filename, "r", encoding="utf-8") as file:
        proxies = file.read().splitlines()
    print(f"Total proxies read from {filename}: {len(proxies)}")
    working_proxies = set()
    unchecked_proxies = set(proxies)
    
    def worker(proxy):
        check_proxy(proxy, working_proxies, unchecked_proxies)
    
    check_threads = [threading.Thread(target=worker, args=(proxy,)) for proxy in proxies]
    for thread in check_threads:
        thread.start()
    for thread in check_threads:
        thread.join()
    input(f"Total working proxies saved: {len(working_proxies)}")
    clear_file(filename)
    remove_duplicates("http_check.txt");remove_duplicates("proxies.txt")

def setup():
    try:
        if not os.path.exists('config.json'):
            config = {"clearcmd": True}
            with open('config.json', 'w') as config_file:
                json.dump(config, config_file, indent=4)
        else:
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
                if "clearcmd" not in config:
                    config["clearcmd"] = True
                    with open('config.json', 'w') as updated_config_file:
                        json.dump(config, updated_config_file, indent=4)
        while True:
            user_input = input("Do you want to enable clear command in the console? (True/False): ").lower()
            if user_input in ["true", "false"]:
                config["clearcmd"] = user_input == "true"
                break
            else:
                print("Invalid input. Please enter 'True' or 'False'.")
        with open('config.json', 'w') as updated_config_file:
            json.dump(config, updated_config_file, indent=4)

        print("Configuration updated successfully.")

    except Exception:
            if not os.path.exists('config.json'):
                config = {"clearcmd": True}
                with open('config.json', 'w') as config_file:
                    json.dump(config, config_file, indent=4)
            else:
                with open('config.json', 'r') as config_file:
                    config = json.load(config_file)
                    if "clearcmd" not in config:
                        config["clearcmd"] = True
                        with open('config.json', 'w') as updated_config_file:
                            json.dump(config, updated_config_file, indent=4)
            os.system('cls' if os.name == 'nt' else 'clear')
            user_input = input("Do you want to enable clear command in the console? (True/False): ").lower()
            if user_input in ["true", "false"]:
                config["clearcmd"] = user_input == "true"
            else:
                print("Invalid input. Please enter 'True' or 'False'.")
                with open('config.json', 'w') as updated_config_file:
                        json.dump(config, updated_config_file, indent=4)
            print("Configuration updated successfully.")

def is_config_setup():
    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            if 'clearcmd' not in config:
                print("Error: 'clearcmd' key not found in config.json.")
                setup()
                return True
            return True
    except FileNotFoundError:
        print("Error: config.json not found.")
        setup();return True
    except json.JSONDecodeError:
        print("Error: config.json is not a valid JSON file.")
        winput = input("Do you want the program to recreate it? (yes/no)")
        if winput == "no":
            setup();return True
        elif winput == "yes":
            if os.path.exists('config.json'):
                os.remove('config.json') if os.name == 'nt' else os.system('rm config.json')

            config = {"clearcmd": True}
            with open('config.json', 'w') as config_file:
                json.dump(config, config_file, indent=4)
                time.sleep(0.5)
                config_file.close()
                print("Configuration file recreated successfully.")
                if os.path.exists('config.json'):
                    os.remove('config.json') if os.name == 'nt' else os.system('rm config.json')
                setup();return True
    except Exception as e:
        print(f"An error occurred while checking config.json: {e}")
        input("AFter pressing enter, the program will close.");exit()

if __name__ == "__main__":
    if is_config_setup():
        update_title("setup")
        clear_file('proxies.txt')
        update_title("start")
        main()
        remove_invalid_proxies("http.txt")
        check_proxies_from_file("http.txt")
    else:
        update_title("start")
        setup()
        clear_file('proxies.txt')
        main()
        remove_invalid_proxies("http.txt")
        check_proxies_from_file("http.txt")