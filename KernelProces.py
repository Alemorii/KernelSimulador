MaxMp = 5 

Particiones = [
    {"nombre": "SO", "tamanio": 100, "proceso": None},
    {"nombre": "GRANDE", "tamanio": 250, "proceso": None},
    {"nombre": "MEDIANO", "tamanio": 150, "proceso": None},
    {"nombre": "PEQUEÑO", "tamanio": 50, "proceso": None}, 
]

class Proceso: 
    def __init__(self, pid, nombre, tamanio):
        self.pid = pid
        self.nombre = nombre
        self.tamanio = tamanio

    def __repr__(self):
        return f"{self.nombre} (PID={self.pid}, {self.tamanio}K)"


def leer_procesos_desde_archivo(ruta_archivo):
    procesos = []  # acá guardamos los procesos que leemos
    
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
            if len(partes) != 3:
                print(f"Linea invalida: {linea}")
                continue

            pid_str, nombre, tamanio_str = partes

            try:
                pid = int(pid_str)          # convertir a entero
                tamanio = int(tamanio_str)  # convertir a entero
            except ValueError: 
                print(f"Datos invalidos en la linea: {linea}")
                continue
            
            # objeto proceso con los datos leídos
            proceso = Proceso(pid, nombre, tamanio)

            # agregamos el proceso a la lista
            procesos.append(proceso)

    return procesos


if __name__ == "__main__":
    procesos = leer_procesos_desde_archivo("procesos.txt") 

    print("Procesos leídos:")
    for p in procesos:
        print(p)  # este es mi codigo
