MaxMp = 5 

Particiones = [
    {"nombre": "SO", "tamanio": 100, "proceso": None },
    {"nombre": "GRANDE", "tamanio": 250, "proceso": None},
    {"nombre": "MEDIANO", "tamanio": 150, "proceso": None},
    {"nombre": "PEQUEÑO", "tamanio": 50, "proceso": None}, 
]

class Proceso: 
    def __init__(self, pid,nombre,tamanio):
        self.pid = pid
        self.nombre = nombre
        self.tamanio = tamanio

    def __repr__(self):
        return f"{self.nombre} (PID={self.pid}, {self.tamano}K"
    
    
