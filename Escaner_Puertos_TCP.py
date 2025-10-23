#Escaner de puertos usando el protocolo TCP

#Librerias
import threading
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple
import argparse
import ipaddress
import subprocess
import platform

class Equipo:
    def __init__(self, ip, timeout: float=0.5, workers: int=500): # Constructor 
        self.ip=ip 
        self.timeout=timeout
        self.workers=workers
        self.open_ports: List[int] = []
        self.mostrar_barra=False
        self.hosts: List[str] = []
    
    def escaner(self,puerto:int) -> Tuple: 
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
    
    def esperar_enter(self):
        while True:
            input()
            self.mostrar_barra=True

    def ping_host(self,ip: str):
        try:
            sistema=platform.system().lower()
            if sistema=="windows":
                param="-n"
            else:
                param="-c"

            result=subprocess.run(['ping',param,'1', ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False
        

    def subred(self, subred: str):
        print(f"Escaneando subred...")
        red=ipaddress.ip_network(subred, strict=False)
        self.hosts=[]

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futuros={executor.submit(self.ping_host, str(ip)): str(ip) for ip in red.hosts()}
            for futures in as_completed(futuros):
                ip=futuros[futures]
                try:
                    activos=futures.result()
                except Exception:
                    activos=False
                if activos:
                    print(f"El host {ip} está activo")
                    self.hosts.append(ip)
        if self.hosts:
            print("Hosts activos encontrados:")
            for h in sorted(self.hosts):
                print(f" - {h}")
        else:
            print("No se encontraron hosts activos.")

    def run(self, puerto_concreto: int, puerto_inicio: int, puerto_final: int=65535): #Revisar este metodo 
        puertos=range(puerto_inicio, puerto_final+1)
        contador = 0
        contador_conc=0
        puerto_conc=puerto_concreto

        hilo_esperar=threading.Thread(target=self.esperar_enter,daemon=True)
        hilo_esperar.start()
        
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            if puerto_concreto is not None:
                futuro_conc={executor.submit(self.escaner,puerto_concreto): puerto_concreto }
                for future_conc in as_completed(futuro_conc):
                    try:
                        p, abierto_conc=future_conc.result()
                    except Exception:
                        abierto_conc=False

                    contador_conc +=1

                    if abierto_conc:
                        print(f"El puerto {p} está abierto")
                        self.open_ports.append(p)

            else:                
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
                    
                    if self.mostrar_barra:
                        #imprimir barra de progreso
                        porcentaje=(contador/65535)*100
                        print(f"Comprobado: {contador}/{65535} ({porcentaje})")
                        self.mostrar_barra=False

        print(f"\n[i] Escaneo completado. Total de puertos abiertos: {len(self.open_ports)}")

def parse_qs():
    parser=argparse.ArgumentParser(description="Escáner TCP sencillo")
    parser.add_argument("ip", nargs='?', help="IP del objetivo a escanear")
    parser.add_argument("--workers", "-w", type=int, default=500, help="Número de hilos (valor por defecto de 500 hilos).")
    parser.add_argument("--timeout", "-t", type=float, default=0.5, help="Tiempo para pasar a estado desconectado")
    parser.add_argument("-i", dest="puerto_inicio", type=int, help="Puerto inicial.")
    parser.add_argument("-f", dest="puerto_final", type=int, help="Puerto final.")
    parser.add_argument("-p", dest="puerto_concreto", type=int, help="Especificar un puerto concreto.")
    parser.add_argument("-o", dest="output", type=str, help="Guardar en un archivo.")
    parser.add_argument("-sn", dest="subred" , help="Escanea la subred proporcionada.")
    args= parser.parse_args()

    if not args.ip and not args.subred:
        parser.error("Debes especificar IP obejtivo o subred con el parámetro -sn")

    if args.ip:
        try:
            ipaddress. ip_address(args.ip)
        except ValueError:
            parser.error(f"[!] IP inválida: {args.ip}")

    if args.subred:
        try:
            ipaddress.ip_network(args.subred, strict=False)
        except ValueError:
            parser.error(f"[!] Subred inválida: {args.subred}")
        
    return args

def main():
    args = parse_qs()

    puerto_inicioo = args.puerto_inicio if args.puerto_inicio is not None else 1
    puerto_finall  = args.puerto_final  if args.puerto_final  is not None else 65535

    if not (1<=puerto_inicioo <= 65535 and 1 <= puerto_finall <= 65535):
        print("[!] Los puertos deben de estar en el rango 1-65535")
        return
    if puerto_inicioo > puerto_finall:
        print("[!] El puerto inicial no puede ser mayor que el puerto final")
        return
    
    if args.puerto_concreto is not None and not (1 <= args.puerto_concreto <= 65535):
        print("[!] El puerto debe de estar en el rango 1-65535")
        return

    if args.subred and not args.ip:
        escaner = Equipo(None, timeout=args.timeout, workers=args.workers)
        escaner.subred(args.subred)
        return
    
    escaner=Equipo(args.ip, timeout=args.timeout, workers=args.workers)
    escaner.run(puerto_concreto=args.puerto_concreto, puerto_inicio=puerto_inicioo, puerto_final=puerto_finall)
    if args.subred:
        escaner.subred(args.subred)

    if args.output:
        try:
            out=args.output
            if out.lower().endswith(".json"):
                import json
                with open(out,"w",encoding="utf-8") as f:
                    json.dump({"ip":args.ip, "puerto": sorted(escaner.open_ports)}, f, indent=2)
            else:
                if out.lower().endswith(".txt"):
                    with open(out,"w",encoding="utf-8") as f:
                        for p in sorted(escaner.open_ports):
                            f.write(f"IP: {args.ip}, Puerto: {p}\n")
            print(f"Fichero guardado en: {out}")
        except Exception as e:
            print(f"[!] No se pudo guardar el fichero")
           
if __name__=="__main__":
    main()


 









                

