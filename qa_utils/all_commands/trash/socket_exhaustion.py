import multiprocessing
import socket



def exaust(task_n):
        TCP_IP = '127.0.0.1'
        TCP_PORT = 10002
        k = 0
        while k < 100:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((TCP_IP, TCP_PORT))
                k += 1
            except:
                continue

if __name__ == '__main__':
    with multiprocessing.Pool(1000) as p:
        p.map(exaust, range(0, 1))