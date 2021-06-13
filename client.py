import socket
import sys
import threading

def read_msg(sock_cli, friend_req_queue):
    while True:
        data = sock_cli.recv(65535)
        if len(data) == 0:
            break
        cmd, message = data.split(b"|", 1)
        cmd = cmd.decode("utf-8")
        if cmd == "message":
            message = message.decode("utf-8")
            print(message)
        elif cmd == "reqfriend":
            friend = message.decode("utf-8")
            friend_req_queue.add(friend)
            print(f"Friend request from {friend}\n"
                  f"type: 'accfriend {friend}' to accept friend request")

sock_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock_cli.connect(("0.0.0.0", 6666))

#kirim username ke server.py
uname = input("Masukkan username: ")
sock_cli.send(bytes(uname, "utf-8"))

friend_req_queue = set()

#buat thread utk membaca pesan dan jalankan threadnya
thread_cli = threading.Thread(target=read_msg, args=(sock_cli, friend_req_queue))
thread_cli.start()

try:
    while True:
        dest = input("Ketik input sesuai format : \n"
                     "- Kirim Pesan (message <username> <message>)\n"
                     "- Pesan Broadcast (bcast <message>)\n"
                     "- Permintaan Pertemanan (reqfriend <username>)\n"
                     "- Terima Pertemanan (accfriend <username>)\n"
                     "- Keluar (exit)\n")
        msg = dest.split(" ", 1)

        if msg[0] == "message":
            uname, message = msg[1].split(" ", 1)
            sock_cli.send(bytes("{}|{}".format(uname, message), "utf-8"))
        elif msg[0] == "bcast":
            sock_cli.send(bytes("bcast|{}".format(msg[1]), "utf-8"))
        elif msg[0] == "reqfriend":
            sock_cli.send(bytes("reqfriend|{}".format(msg[1]), "utf-8"))
        elif msg[0] == "accfriend":
            friend = msg[1]
            if friend in friend_req_queue:
                friend_req_queue.remove(friend)
                sock_cli.send(bytes("accfriend|{}".format(friend), "utf-8"))
            else:
                print("username not detected")
        elif msg[0] == "exit":
            sock_cli.close()
            break

except KeyboardInterrupt:
    sock_cli.close()
    sys.exit(0)