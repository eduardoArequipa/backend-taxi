import enum

class RolUsuario(str, enum.Enum):
    pasajero = "pasajero"
    conductor = "conductor"
    operador = "operador"

class EstadoViaje(str, enum.Enum):
    pendiente = "pendiente"

    en_curso = "en_curso"
    finalizado = "finalizado"
    cancelado = "cancelado"
