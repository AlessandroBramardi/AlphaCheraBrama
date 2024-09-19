import socket
MYADDRESS = ("192.168.1.125", 9090)
BUFFER_SIZE = 4096

def avanti(val):
    print(f"Sono andato avanti di {val}")
    return f"sono andato avanti di {val}"
def indietro(val):
    print(f"Sono andato indietro di {val}")
    return f"sono andato indietro di {val}"
def left(val):
    print(f"Sono andato a sinistra di {val}")
    return f"sono andato a sinistra di {val}"
def right(val):
    print(f"Sono andato a destra di {val}")
    return f"sono andato a destra di {val}"

def main():    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(MYADDRESS)
    s.listen()
    diz_comandi={"forward":avanti,"backward":indietro,"left":left,"right":right} #diz con funzioni relative al comando
    connection, client_address = s.accept()
    status = ""
    print(f"The client {client_address} is connected")
    while True:
        data= connection.recv(BUFFER_SIZE).decode()
        comando, val = data.split("|")
        if comando not in diz_comandi:
            status = "error"
            connection.sendall(f"{status}|comand non in list".encode())
        else:
            risposta = diz_comandi[comando](val)
            status = "ok"
            connection.sendall(f"{status}|{risposta}".encode())
        
if __name__ == '__main__':
    main()
