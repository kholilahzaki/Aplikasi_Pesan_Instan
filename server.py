import socket
import sys
import threading


def read_msg(clients, friends, sock_cli, addr_cli, src_uname):
    while True:
        data = sock_cli.recv(65535)
        if len(data) == 0:
            break

        #parsing pesannya
        dest, msg = data.split(b"|", 1)
        dest = dest.decode("utf-8")

        #kirim pesan ke semua client
        if dest == "reqfriend":
            dest_uname = msg.decode("utf-8")
            if dest_uname in clients:
                send_friend_request(clients[dest_uname][0], src_uname)
            else:
                send_msg(clients[src_uname][0], "{} not in clients".format(dest_uname))
        elif dest == "accfriend":
            dest_uname = msg.decode("utf-8")
            friends[src_uname].append(dest_uname)
            friends[dest_uname].append(src_uname)
            send_msg(clients[dest_uname][0], "{} is now friends.".format(src_uname))
            send_msg(clients[src_uname][0], "{} is now friends.".format(dest_uname))
        elif dest == "bcast":
            msg = msg.decode("utf-8")
            _msg = "<{}>: {}".format(src_uname, msg)
            send_broadcast(clients, friends, src_uname, _msg, addr_cli)
        else:
            dest_uname = dest
            msg = msg.decode("utf-8")
            _msg = "<{}>: {}".format(src_uname, msg)
            dest_sock_cli = get_sock(clients, friends, src_uname, dest_uname)
            if dest_sock_cli is not None:
                send_msg(dest_sock_cli, _msg)
    sock_cli.close()
    print("connection closed", addr_cli)
    del clients[src_uname]


def send_broadcast(clients, friends, src_uname, data, sender_addr_cli):
    cur_friends = friends[src_uname]
    for cur_friend in cur_friends:
        if cur_friend not in clients:
            continue
        sock_cli, addr_cli, _ = clients[cur_friend]
        if not (sender_addr_cli[0] == addr_cli[0] and sender_addr_cli[1] == addr_cli[1]):
            send_msg(sock_cli, data)


def send_friend_request(sock_cli, src_uname):
    sock_cli.send(bytes("reqfriend|{}".format(src_uname), "utf-8"))


def send_msg(sock_cli, data):
    sock_cli.send(bytes("message|{}".format(data), "utf-8"))


def get_sock(clients, friends, src_uname, dest_uname):
    if dest_uname not in friends[src_uname]:
        send_msg(clients[src_uname][0], "Error: {} not a friend".format(dest_uname))
        return None
    if dest_uname not in clients:
        send_msg(clients[src_uname][0], "Error: {} not in clients".format(dest_uname))
        return None
    return clients[dest_uname][0]


server_address = ("0.0.0.0", 6666)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(server_address)
server_socket.listen(5)

# buat dictionary utk menyimpan informasi
clients = {}
friends = {}

try:
    while True:
        sock_cli, addr_cli = server_socket.accept()

        # membaca username client
        src_uname = sock_cli.recv(65535).decode("utf-8")
        print(src_uname, "joined")

        # membuat thread
        thread_cli = threading.Thread(target=read_msg, args=(clients, friends, sock_cli, addr_cli, src_uname))
        thread_cli.start()

        # simpan informasi client ke dictionary
        clients[src_uname] = (sock_cli, addr_cli, thread_cli)
        friends[src_uname] = []

except KeyboardInterrupt:
    server_socket.close()
    sys.exit(0)