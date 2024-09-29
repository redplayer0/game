import socket
from threading import Thread
from uuid import uuid4

games = {}
clients = []

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


class Game:
    def __init__(self, *, id: str, player_1, player_2):
        self.id = id
        self.player_1 = player_1
        self.player_2 = player_2
        self.disconnected_player = None

    def start(self):
        Thread(target=self.listen, args=[self.player_1], daemon=True).start()
        Thread(target=self.listen, args=[self.player_2], daemon=True).start()

    def handle_msg(self, msg):
        print(msg.upper())

    def listen(self, player):
        while not self.disconnected_player:
            msg = player.recv(1024).decode("utf-8")
            if msg:
                self.handle_msg(msg)
            else:
                self.disconnected_player = player
                break


if __name__ == "__main__":
    ip = "localhost"
    port = 8888
    sock.bind((ip, port))
    sock.listen(5)
    print("listening..")
    while True:
        conn, addr = sock.accept()
        clients.append(conn)
        if len(clients) > 1:
            game_id = uuid4()
            new_game = Game(
                id=game_id,
                player_1=clients.pop(),
                player_2=clients.pop(),
            )
            games[game_id] = new_game
            new_game.start()
        else:
            conn.send("wait for opponent".encode())
