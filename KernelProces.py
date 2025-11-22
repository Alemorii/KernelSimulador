MaxMp = 5
Ejecucion = False
instante = 0
listos_max = 2
listo_susp_max = 2

# colas globales
procesos_listos = []
procesos_listo_suspendido = []
procesos_ejecucion = []

Particiones = [
    {"id": 0, "nombre": "SO", "inicio": 0,   "tamanio": 100, "proceso": "SO",  "frag_int": 0},
    {"id": 1, "nombre": "GRANDE",  "inicio": 100, "tamanio": 250, "proceso": None, "frag_int": 250},
    {"id": 2, "nombre": "MEDIANA", "inicio": 350, "tamanio": 150, "proceso": None, "frag_int": 150},
    {"id": 3, "nombre": "PEQUEÑA", "inicio": 500, "tamanio": 50,  "proceso": None, "frag_int": 50},
]


class Proceso:
    def __init__(self, pid, tiempo_arribo, tiempo_irrupcion, tamanio):
        self.pid = pid
        self.tiempo_arribo = tiempo_arribo
        self.tiempo_irrupcion = tiempo_irrupcion
        self.tiempo_restante = tiempo_irrupcion
        self.tamanio = tamanio
        self.nombre = f"P_{pid}"

        self.estado = 'nuevo'
        self.particion_id = None

        # tiempos para mediciones
        self.tiempo_comienzo = None
        self.tiempo_fin = None
        self.tiempo_espera = 0
        self.ultima_vez_listo = None

    def __repr__(self):
        return (f"{self.nombre} (PID={self.pid}, arribo={self.tiempo_arribo},"
                f"irrupcion={self.tiempo_irrupcion} tamanio={self.tamanio}K), "
                f"restante={self.tiempo_restante}")


def leer_procesos_desde_archivo(ruta_archivo):
    cola_nuevos = []

    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            for linea in archivo:
                linea = linea.strip()
                if not linea or linea.startswith('#'):
                    continue

                partes = linea.split()
                if len(partes) != 4:
                    print(f"No cumple con los 4 campos: {linea}")
                    continue

                pid_str, arribo_str, irrupcion_str, tamanio_str = partes

                try:
                    pid = int(pid_str)
                    arribo = int(arribo_str)
                    irrup = int(irrupcion_str)
                    tamanio = int(tamanio_str)
                except ValueError:
                    print(f"Datos inválidos en la línea: {linea}")
                    continue

                proceso = Proceso(pid, arribo, irrup, tamanio)
                cola_nuevos.append(proceso)
    except FileNotFoundError:
        print(f"No se encontró el archivo: {ruta_archivo}")
    return cola_nuevos


def contar_en_sistema():
    return len(procesos_ejecucion) + len(procesos_listos) + len(procesos_listo_suspendido)


def best_fit(proceso):
    mejor_particion = None
    mejor_frag = None

    for part in Particiones:
        # si la partición está ocupada por un proceso (y no es el SO), la salto
        if part["proceso"] is not None and part["proceso"] != "SO":
            continue

        if proceso.tamanio <= part["tamanio"]:
            frag_int = part["tamanio"] - proceso.tamanio

            if mejor_frag is None or frag_int < mejor_frag:
                mejor_particion = part
                mejor_frag = frag_int

    if mejor_particion is None:
        return False

    mejor_particion["proceso"] = proceso
    mejor_particion["frag_int"] = mejor_frag
    proceso.particion_id = mejor_particion["id"]

    return True


def tratar_nuevos(cola_nuevos, instante):
    global Ejecucion, procesos_listos, procesos_listo_suspendido, procesos_ejecucion

    cola_actual = []
    cola_sobrante = []

    for p in cola_nuevos:
        if p.tiempo_arribo == instante and p.estado == 'nuevo':
            cola_actual.append(p)

            # 1) control de multiprogramación
            if contar_en_sistema() >= MaxMp:
                # no puede entrar al sistema aún, lo marcamos como sobrante
                p.estado = 'nuevo'
                cola_sobrante.append(p)
                continue

            # 2) intentar asignar partición
            puede_entrar = best_fit(p)

            if puede_entrar:
                if not Ejecucion:
                    p.estado = 'ejecucion'
                    Ejecucion = True
                    procesos_ejecucion.append(p)
                else:
                    if len(procesos_listos) < listos_max:
                        p.estado = 'listo'
                        procesos_listos.append(p)
                    else:
                        if len(procesos_listo_suspendido) < listo_susp_max:
                            p.estado = 'listo/suspendido'
                            procesos_listo_suspendido.append(p)
                        else:
                            # esto solo pasa si MaxMp y los límites están descoordinados
                            p.estado = 'nuevo'
                            cola_sobrante.append(p)
            else:
                # no entra en ninguna partición
                if len(procesos_listo_suspendido) < listo_susp_max and contar_en_sistema() < MaxMp:
                    p.estado = 'listo/suspendido'
                    procesos_listo_suspendido.append(p)
                else:
                    p.estado = 'nuevo'
                    cola_sobrante.append(p)

    return cola_actual, cola_sobrante


def ejecutar_tick(instante):
    global Ejecucion,procesos_ejecucion

    if not procesos_ejecucion:
        return #cpu osicosa
    
    p = procesos_ejecucion[0] # solo puede haber uno en ejecucion

    if p.tiempo_comienzo is None:
        p.tiempo_comienzo = instante

    p.tiempo_restante -= 1

    if p.tiempo_restante <= 0:
        p.tiempo_fin = instante +1 # termino en este tick
        p.estado= 'terminado'
        liberar_particion(p)
        procesos_ejecucion.remove(p)
        Ejecucion=False

def liberar_particion(proceso):
    if proceso.particion_id is None:
        return
    for part in Particiones:
        if part["id"] == proceso.particion_id:
            part["proceso"] = None
            part["frag_int"] = part["tamanio"]
            proceso.particion_id = None
            break



if __name__ == "__main__":
    cola_nuevos = leer_procesos_desde_archivo("procesos.txt")

    instante = 0
    cola_actual, cola_sobrantes = tratar_nuevos(cola_nuevos, instante)

    print("Procesos leídos:")
    for p in cola_nuevos:
        print(p)

    print(f"Llegaron en t={instante}:", cola_actual)
    print("Sobrantes (no entraron por multiprogramación):", cola_sobrantes)
    print("Ejecucion:", procesos_ejecucion)
    print("Listos:", procesos_listos)
    print("Listo/Suspendido:", procesos_listo_suspendido)
