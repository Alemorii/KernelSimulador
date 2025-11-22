MaxMp = 5
Ejecucion = False
instante = 0

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
    cola_nuevos = []  # acá guardamos los procesos que leemos

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
                cola_nuevos.append(proceso)
    except FileNotFoundError:
        print(f"No se encontró el archivo: {ruta_archivo}")
    return cola_nuevos


def tratar_nuevos(cola_nuevos, instante):
    cola_actual= []
    for p in cola_nuevos: 
        if p.tiempo_arribo == instante and p.estado== 'nuevo':
            cola_actual.append(p)
            if Ejecucion == False: 
                p.estado = 'Ejecucion'
                Ejecucion = True
            else:
                p.estado= 'listo'
    return cola_actual
    

#def tratar_listos(cola_actual):
    #for p in cola_actual:

if __name__ == "__main__":
    cola_nuevos = leer_procesos_desde_archivo("procesos.txt")

    print("Procesos leídos:")
    for p in cola_nuevos:
        print(p)
