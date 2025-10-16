#Escaner de puertos usando el protocolo TCP

#Librerias
from ast import arguments
import socket
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple
import argparse
import ipaddress

class Equipo:
    def __init__(self, ip, timeout: float=0.5, workers: int=500): # Crea constructor 
        self.ip=ip #Al objeto creado le asigna esta variable
        self.timeout=timeout
        self.workers=workers
        self.open_ports: List[int] = []
    
    def escaner(self,puerto:int) -> Tuple: #Devuelve una tupla
        conexion=socket.socket(socket.AF_INET,socket.SOCK_STREAM) # Crea una conexion TCP
        conexion.settimeout(self.timeout)
        try:
            result=conexion.connect_ex((self.ip,puerto)) #Se conecta a la Ip y puerto correspondiente
            return puerto, (result==0)
        except Exception:
            return puerto, False
        finally:
            try:
                conexion.close()
            except Exception:
                pass
        
    def run(self, puerto_inicio: int=1, puerto_final: int=65535):
        puertos=range(puerto_inicio, puerto_final+1)
        total=puerto_final-puerto_inicio+1
        contador = 0

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futuro={executor.submit(self.escaner,p): p for p in puertos}
            for future in as_completed(futuro):
                puerto=futuro[future]
                try:
                    p, abierto=future.result()
                except Exception:
                    abierto=False

                contador +=1

                if abierto:
                    print(f"El puerto {p} está abierto")
                    self.open_ports.append(p)
                
        print(f"\n[i] Escaneo completado. Total de puertos abiertos: {len(self.open_ports)}")

def parse_qs():
    parser=argparse.ArgumentParser(description="Escáner TCP sencillo")
    parser.add_argument("ip", help="IP del objetivo a escanear")
    parser.add_argument("--workers", "-w", type=int, default=500, help="Número de hilos (valor por defecto de 500 hilos)")
    parser.add_argument("--timeout", "-t", type=float, default=0.5, help="Tiempo para pasar a estado desconectado")
    parser.add_argument("-i", dest="puerto_inicio", type=int, help="Puerto inicial")
    parser.add_argument("-e", dest="puerto_final", type=int, help="Puerto final")

    return parser.parse_args()
    

def main():
    args = parse_qs()

    try:
        ipaddress.IPv4Address(args.ip)
    except Exception:
        print(f"[!] IP invalida: {args.ip}")
        return

    if not (1<=args.puerto_inicio <= 65535 and 1 <= args.puerto_final <= 65535):
        print("[!] Los puertos deben de estar en el rango 1-65535")
        return

    if args.puerto_inicio > args.puerto_final:
        print("[!] El puerto inicial no puede ser mayor que el puerto final")
        return

    escaner=Equipo(args.ip , timeout=args.timeout, workers=args.workers)
    escaner.run(puerto_inicio=args.puerto_inicio ,puerto_final=args.puerto_final)

if __name__=="__main__":
    main()


 









                

