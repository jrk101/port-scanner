import socket
import threading
from queue import Queue

port_queue = Queue()
sock_timeout = 1
num_threads = 100
lock = threading.Lock()

def get_service(port):
    try:
        return socket.getservbyport(port)
    except:
        return "Unknown"

def scan_ports(target, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(sock_timeout)
        result = sock.connect_ex((target, port))
        with lock:
            if result == 0:
                service = get_service(port)
                print(f"[OPEN] Port: {port:>5} | Service: {service}")
    except Exception as e:
        with lock:
            print(f"Could not scan port {port}: {e}")

def thread_runner(ip):
    while not port_queue.empty():
        port = port_queue.get()
        scan_ports(ip, port)
        port_queue.task_done()

def run_scanner(ip, port_range):
    print(f"[*] Scanning {ip} from port {port_range[0]} to {port_range[1]}...\n")

    for port in range(port_range[0], port_range[1] + 1):
        port_queue.put(port)

    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=thread_runner, args=(ip,))
        t.daemon = True
        t.start()
        threads.append(t)

    port_queue.join()
    print("\n[*] Scan completed.")

if __name__ == "__main__":
    port_range = (1, 1024)
    ip = input("Enter the IP or domain to scan: ")
    try:
        resolved_ip = socket.gethostbyname(ip)
        run_scanner(resolved_ip, port_range)
    except socket.gaierror:
        print("Invalid IP or domain.")
