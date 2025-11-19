MaxMp = 5 

Particiones = [
    {"id": 0, "nombre": "SO", "inicio":0, "tamanio":100, "proceso":"SO", "frag_int" :0},
    {"id": 1, "nombre": "GRANDE", "inicio":100, "tamanio":250,"proceso":None, "frag_int" :250},
    {"id": 2, "nombre": "MEDIANA", "inicio":350, "tamanio":150,"proceso":None, "frag_int" :120},
    {"id": 3, "nombre": "PEQUEÑA", "inicio":500, "tamanio":50,"proceso":None, "frag_int" :60},
]

class Proceso: 
    def __init__(self, pid, tiempo_arribo,tiempo_irrupcion, tamanio):
        self.pid = pid
        self.tiempo_arribo = tiempo_arribo
        self.tiempo_irrupcion = tiempo_irrupcion
        self.tiempo_restante = tiempo_irrupcion
        self.tamanio = tamanio
        self.nombre = f"P_{pid}"

        self.estado= 'nuevo'

        #tiempo para mediciones
        self.tiempo_comienzo = None 
        self.tiempo_fin= None 
        self.tiempo_espera = 0
        self.ultima_vez_listo= None 

    def __repr__(self):
        return (f"{self.nombre} (PID={self.pid}, arribo={self.tiempo_arribo},"
        f"irrupcion= {self.tiempo_irrupcion}tamanio={self.tamanio}K), "
        f"restante={self.tiempo_irrupcion}")


def leer_procesos_desde_archivo(ruta_archivo):
    procesos = []  # acá guardamos los procesos que leemos
    
    try:
        # abrir el archivo 
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            # recorrer línea por línea
            for linea in archivo:
                linea = linea.strip()

                # ignorar líneas vacías o comentarios
                if not linea or linea.startswith('#'):
                    continue 

                # separar la línea por espacios
                partes = linea.split()

                # esperamos exactamente 3 elementos: PID NOMBRE TAMANIO
                if len(partes) != 4:
                    print(f"No cumple con los 4 campos: {linea}")
                    continue

                pid_str, arribo_str, irrupcion_str, tamanio_str = partes

                try:
                    pid = int(pid_str)
                    arribo= int(arribo_str)
                    irrup= int(irrupcion_str)          # convertir a entero
                    tamanio = int(tamanio_str)  # convertir a entero
                except ValueError: 
                    print(f"Datos invalidos en la linea: {linea}")
                    continue
                
                # objeto proceso con los datos leídos
                proceso = Proceso(pid, arribo,irrup, tamanio)

                # agregamos el proceso a la lista
                procesos.append(proceso)
                if len(procesos) >= MaxMp:
                    print("se alcanzo el maximo de proceso a multiprogramar")
                    break
    except FileNotFoundError:
        print(f"No se encontró el archivo: {ruta_archivo}")
    return procesos


if __name__ == "__main__":
    procesos = leer_procesos_desde_archivo("procesos.txt") 

    print("Procesos leídos:")
    for p in procesos:
        print(p)  