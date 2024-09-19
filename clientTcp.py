import socket
SERVER_ADDRESS=("192.168.1.125",9090)
BUFFER_SIZE=4096

def main():
    diz ={"0":"quit", "1":"forward", "2":"backward", "3":"left", "4":"right"}
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(SERVER_ADDRESS)
    while True:
            print("choose your move:")
            print(diz)
            
            choice = input("choose the number-> ")
            if choice == '0':
                break
            elif choice in diz:
                time = int(input("choose the time in seconds -> "))
                # Invia il comando al server
                s.sendall(f"{str(diz[choice])}|{str(time)}".encode())
                # Ricevi la risposta dal server (se necessaria)
                data = s.recv(1024)
                print(f"{data.decode().replace(f"|",": ")}")
            else:
                print(f"{choice} not in diz")

if __name__=="__main__":
    main()