import sys
import os

#ambiente inicial
MaxMp = 5
Ejecucion = False
instante = 0
listos_max = 2
listo_susp_max = 2

# Colas globales
procesos_listos = []
procesos_listo_suspendido = []
procesos_ejecucion = []
procesos_terminados = []

# Particiones fijas
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
        self.nombre = f"P{pid}" # Formato P1, P2 
        self.estado = 'nuevo'
        self.particion_id = None
        
        # Estadísticas
        self.tiempo_comienzo = None
        self.tiempo_fin = None
        self.tiempo_retorno = 0
        self.tiempo_espera_calc = 0 

    def __repr__(self):
        return self.nombre

# --- funciones de tabulacion ---

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def dibujar_tabla_particiones():
    print(f"\n{'PARTICIÓN':^10}|{'CONTENIDO':^20}|{'TAMAÑO PARTICIÓN':^18}|{'FI/FE/EL':^15}")
    print("-" * 66)
    
    # Fila SO
    print(f"{0:^10}|{'Sistema operativo':^20}|{'100 KB':^18}|{'FI: 0 KB':^15}")
    print("-" * 66)

    for part in Particiones:
        if part["nombre"] == "SO": continue
        
        id_p = part["id"]
        tam_p = f"{part['tamanio']} KB"
        
        if part["proceso"] is not None:
            proc = part["proceso"]
            contenido = f"{proc.nombre}({proc.tamanio} KB)"
            fi = f"FI: {part['frag_int']} KB"
        else:
            contenido = "Libre"
            fi = f"FI: {part['tamanio']} KB"
            
        print(f"{id_p:^10}|{contenido:^20}|{tam_p:^18}|{fi:^15}")
        print("-" * 66)

def mostrar_estado_sistema(instante, cola_nuevos_originales):
    # Clasificar procesos para mostrar en las listas
    p_ejec = [p.nombre for p in procesos_ejecucion]
    p_listos = [p.nombre for p in procesos_listos]
    p_susp = [p.nombre for p in procesos_listo_suspendido]
    p_term = [p.nombre for p in procesos_terminados]
    
    # Filtrar nuevos pendientes y futuros
    p_nuevos = [p.nombre for p in cola_nuevos_originales if p.estado == 'nuevo' and p.tiempo_arribo <= instante]
    p_sin_arribar = [p.nombre for p in cola_nuevos_originales if p.tiempo_arribo > instante]

    print(f"\nINSTANTE: {instante}")
    print("ESTADOS DE LOS PROCESOS:")
    print(f" - EJECUTANDOSE: {', '.join(p_ejec) if p_ejec else 'Ninguno'}")
    print(f" - LISTOS: {', '.join(p_listos) if p_listos else 'Ninguno'}")
    print(f" - LISTOS Y SUSPENDIDOS: {', '.join(p_susp) if p_susp else 'Ninguno'}")
    print(f" - NUEVOS: {', '.join(p_nuevos) if p_nuevos else 'Ninguno'}")
    print(f" - SIN ARRIBAR: {', '.join(p_sin_arribar) if p_sin_arribar else 'Ninguno'}")
    print(f" - TERMINADOS: {', '.join(p_term) if p_term else 'Ninguno'}")
    print() 
    
    dibujar_tabla_particiones()

def imprimir_reporte_final_imagen(procesos_terminados, instante_final):
    limpiar_pantalla()
    print("PRESIONE ENTER PARA CONTINUAR\n")
    input() 
    
    print("NO HAY MÁS PROCESOS ESPERANDO PARA ARRIBAR\n")
    print("DATOS PARA ESTADÍSTICAS:")
    
    total_espera = 0
    total_retorno = 0
    
    # Ordenar por PID para la lista
    procesos_ordenados = sorted(procesos_terminados, key=lambda x: x.pid)
    
    for p in procesos_ordenados:
        # Cálculos finales
        p.tiempo_retorno = p.tiempo_fin - p.tiempo_arribo
        p.tiempo_espera_calc = p.tiempo_retorno - p.tiempo_irrupcion
        
        total_espera += p.tiempo_espera_calc
        total_retorno += p.tiempo_retorno
        
        print(f"{p.nombre}, TAMAÑO: {p.tamanio}, TI INICIAL: {p.tiempo_comienzo}, "
              f"TI FINAL: {p.tiempo_fin}, TI NETO: {p.tiempo_irrupcion}, TA: {p.tiempo_arribo}")

    n = len(procesos_terminados)
    prom_espera = total_espera / n if n > 0 else 0
    prom_retorno = total_retorno / n if n > 0 else 0

    print("\nESTADÍSTICAS:\n")
    print(f" - TOTAL DE PROCESOS EJECUTADOS: {n}")
    print(f"\n - TIEMPO DE ESPERA PROMEDIO: {prom_espera} UT")
    print(f" - TIEMPO DE RETORNO PROMEDIO: {prom_retorno} UT")
    
    print("\n\nPRESIONE ENTER PARA FINALIZAR")
    input()

# --- logica del gestor de procesos ---

def leer_procesos_desde_archivo(ruta_archivo):
    cola_nuevos = []
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            for linea in archivo:
                linea = linea.strip()
                if not linea or linea.startswith('#'): continue
                partes = linea.split()
                if len(partes) != 4: continue
                try:
                    pid, arribo, irrup, tamanio = map(int, partes)
                    cola_nuevos.append(Proceso(pid, arribo, irrup, tamanio))
                except ValueError: continue
    except FileNotFoundError:
        print(f"No se encontró el archivo: {ruta_archivo}")
    return cola_nuevos

def contar_en_sistema():
    return len(procesos_ejecucion) + len(procesos_listos) + len(procesos_listo_suspendido)

def best_fit(proceso):
    mejor_particion = None
    mejor_frag = None
    for part in Particiones:
        if part["proceso"] is not None and part["proceso"] != "SO": continue
        if proceso.tamanio <= part["tamanio"]:
            frag_int = part["tamanio"] - proceso.tamanio
            if mejor_frag is None or frag_int < mejor_frag:
                mejor_particion = part
                mejor_frag = frag_int
    
    if mejor_particion is None: return False
    
    part_id = mejor_particion["id"]
    mejor_particion["proceso"] = proceso
    mejor_particion["frag_int"] = mejor_frag
    proceso.particion_id = part_id
    return True

def tratar_nuevos(cola_nuevos_ref, instante):
    """Intenta mover procesos de NUEVO a LISTO (RAM) o SUSPENDIDO (DISCO)."""
    pendientes = [p for p in cola_nuevos_ref if p.tiempo_arribo <= instante and p.estado == 'nuevo']
    
    for p in pendientes:
        # 1. Control de Multiprogramación Global
        if contar_en_sistema() >= MaxMp:
            continue 
        ingresado_a_ram = False
        
        if len(procesos_listos) < listos_max:
            if best_fit(p):
                p.estado = 'listo'
                procesos_listos.append(p)
                ingresado_a_ram = True
        
        # 3. Si no entró a RAM (por lista llena o particiones llenas), va a DISCO
        if not ingresado_a_ram:
            if len(procesos_listo_suspendido) < listo_susp_max:
                p.estado = 'listo/suspendido'
                procesos_listo_suspendido.append(p)

def check_swap_in():
    """Intenta subir procesos de SUSPENDIDO a LISTO si se liberó espacio."""
    global procesos_listos, procesos_listo_suspendido
    
    # Si no hay nadie en disco, no hacemos nada
    if not procesos_listo_suspendido:
        return

    if len(procesos_listos) >= listos_max:
        return

    # Usamos copia para poder modificar la lista original dentro del loop
    candidatos = list(procesos_listo_suspendido)
    for p in candidatos:
        # Doble chequeo por seguridad dentro del bucle
        if len(procesos_listos) >= listos_max:
            break

        if best_fit(p):
            procesos_listo_suspendido.remove(p)
            p.estado = 'listo'
            procesos_listos.append(p)

def liberar_particion(proceso):
    if proceso.particion_id is None: return
    for part in Particiones:
        if part["id"] == proceso.particion_id:
            part["proceso"] = None
            part["frag_int"] = part["tamanio"]
            proceso.particion_id = None
            break
    
    # Al liberar espacio, verificamos inmediatamente si alguien puede entrar (Swap In)
    check_swap_in()

def seleccionar_proceso_SRTF():
    global Ejecucion, procesos_listos, procesos_ejecucion

    # Candidatos = Listos + El que se está ejecutando actualmente
    candidatos = list(procesos_listos)
    if procesos_ejecucion:
        candidatos.append(procesos_ejecucion[0])

    # Si no hay nadie, la CPU queda ociosa
    if not candidatos:
        Ejecucion = False
        return None

    # Algoritmo SRTF: Menor tiempo restante
    elegido = min(candidatos, key=lambda p: p.tiempo_restante)

    # Si el elegido ya es el que está ejecutando, sigue igual
    if procesos_ejecucion and procesos_ejecucion[0] is elegido:
        return elegido

    # Si hay cambio de contexto (Expropiación o CPU vacía tomaba uno nuevo)
    if procesos_ejecucion:
        actual = procesos_ejecucion.pop(0)
        actual.estado = 'listo'
        procesos_listos.append(actual)

    if elegido in procesos_listos:
        procesos_listos.remove(elegido)

    elegido.estado = 'ejecucion'
    procesos_ejecucion.append(elegido)
    Ejecucion = True
    return elegido

def ejecutar_tick(instante):
    global Ejecucion, procesos_ejecucion
    
    if not procesos_ejecucion:
        return None 

    p = procesos_ejecucion[0]
    
    # Registrar primer uso de CPU
    if p.tiempo_comienzo is None:
        p.tiempo_comienzo = instante

    p.tiempo_restante -= 1

    if p.tiempo_restante <= 0:
        p.tiempo_fin = instante + 1
        p.estado = 'terminado'
        liberar_particion(p)
        procesos_ejecucion.remove(p)
        Ejecucion = False
        return p 
    
    return None 

def iniciar_simulacion(cola_nuevos_originales):
    global instante, procesos_terminados
    
    total_procesos = len(cola_nuevos_originales)
    
    while len(procesos_terminados) < total_procesos:
        limpiar_pantalla()
        
        # cargamos nuevos y hacemos swap-in si corresponde
        tratar_nuevos(cola_nuevos_originales, instante)
        
        # El planificador decide quién ocupa la CPU en este instante
        seleccionar_proceso_SRTF()
        
        # Mostramos cómo quedó el tablero despues de planificar, pero ANTES de ejecutar el tick
        mostrar_estado_sistema(instante, cola_nuevos_originales)
        print("\nPRESIONE ENTER PARA CONTINUAR")
        input() 
        
        # La CPU trabaja 1 unidad de tiempo
        proceso_finalizado = ejecutar_tick(instante)
        if proceso_finalizado:
            procesos_terminados.append(proceso_finalizado)
        
        instante += 1

    return instante


if __name__ == "__main__":
    cola_nuevos = leer_procesos_desde_archivo("procesos.txt")
    
    if cola_nuevos:
        tiempo_final = iniciar_simulacion(cola_nuevos)
        imprimir_reporte_final_imagen(procesos_terminados, tiempo_final)
    else:
        print("No hay procesos para simular o archivo 'procesos.txt' no encontrado.")
