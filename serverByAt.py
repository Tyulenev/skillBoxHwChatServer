"""
Серверное приложение для соединений
"""
import asyncio
from asyncio import transports


class ClientProtocol(asyncio.Protocol):
    login: str
    server: 'Server'
    transport: transports.Transport

    def __init__(self, server: 'Server'):
        self.server = server
        self.login = None

    def data_received(self, data: bytes):
        decoded = data.decode()
        print(decoded)

        # формируем список логинов
        count_of_users = len(self.server.clients)
        loginList: list
        loginList=[]


        for i in range(count_of_users):
            loginList.append(self.server.clients[i].login)

        if self.login is None:
            # login:User
            if decoded.startswith("login:"):
                self.login = decoded.replace("login:", "").replace("\r\n", "")

                #test block
                #print(self.server.clients[0].login)
                #print("self login - ", self.login)
                #end test block

                for login1 in loginList:
                    if login1 == self.login:
                        self.transport.write(
                            f"Логин, {self.login} занят!".encode()
                        )
                        self.connection_lost(exception=NameError)
                        break

                    if login1 == loginList[-1]:
                        self.transport.write(
                            f"Привет, {self.login}!".encode()
                        )
                        self.send_history()

        else:
            self.send_message(decoded)

    def send_history(self):
        count_messages = len(self.server.message_list)
        #print("count messages - ", count_messages)
        if count_messages < 10:
            for cur_mes in self.server.message_list:
                self.transport.write((cur_mes+"\n").encode())
        else:
            for i in range(count_messages - 10, count_messages):
                self.transport.write((self.server.message_list[i]+"\n").encode())


    def send_message(self, message):
        format_string = f"<{self.login}> {message}"

        #ADDed!!!!
        self.server.message_list.append(format_string)

        encoded = format_string.encode()

        for client in self.server.clients:
            if client.login != self.login:
                client.transport.write(encoded)

    def connection_made(self, transport: transports.Transport):
        self.transport = transport
        self.server.clients.append(self)
        print("Соединение установлено")

    def connection_lost(self, exception):
        self.server.clients.remove(self)
        print(f"Соединение разорвано c клиентом {self.login}")



class Server:
    clients: list
    message_list: list

    def __init__(self):
        self.clients = []
        self.message_list = []

    def create_protocol(self):
        return ClientProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.create_protocol,
            "127.0.0.1",
            8888
        )

        print("Сервер запущен ...")

        await coroutine.serve_forever()


process = Server()
try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Сервер остановлен вручную")
