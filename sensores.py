from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from statistics import mean
from typing import Protocol, List


class Notificador(Protocol):
    def enviar(self, mensaje: str) -> None:
        ...


class NotificadorEmail:
    def __init__(self, destinatario: str) -> None:
        self._destinatario = destinatario  # encapsulado

    def enviar(self, mensaje: str) -> None:
        print(f"[EMAIL a {self._destinatario}] {mensaje}")


class NotificadorWebhook:
    def __init__(self, url: str) -> None:
        self._url = url

    def enviar(self, mensaje: str) -> None:
        print(f"[WEBHOOK {self._url}] {mensaje}")


@dataclass
class Sensor(ABC):
    id: str
    ventana: int = 5
    _calibracion: float = field(default=0.0, repr=False)  # encapsulado
    _buffer: list[float] = field(default_factory=list, repr=False)

    # Ejercicio Sensor1
    def leer(self, valor: float) -> None:
        """Agrega lectura aplicando calibración y mantiene ventana móvil."""
        v = valor + self._calibracion
        self._buffer.append(v)
        if len(self._buffer) > self.ventana:
            self._buffer.pop(0)

    @property
    def promedio(self) -> float:
        return mean(self._buffer) if self._buffer else 0.0

    @abstractmethod
    def en_alerta(self) -> bool:
        ...


@dataclass
class SensorTemperatura(Sensor):
    umbral: float = 80.0

    def en_alerta(self) -> bool:
        # Polimorfismo: cada sensor define su propia condición
        return self.promedio >= self.umbral


@dataclass
class SensorVibracion(Sensor):
    rms_umbral: float = 2.5

    def en_alerta(self) -> bool:
        # Ejemplo tonto de RMS ≈ promedio absoluto
        return abs(self.promedio) >= self.rms_umbral
    
@dataclass
class SensorHumedad(Sensor):
    humedad_max: float = 70.0

    def en_alerta(self) -> bool:
        return self.promedio >= self.humedad_max
    
@dataclass
class SensorContaminacionAire(Sensor):
    umbral_particulas_por_millon: float = 100.0

    def en_alerta(self) -> bool:
        return self.promedio >= self.umbral_particulas_por_millon

class GestorAlertas:
    def __init__(self, sensores: List[Sensor], notificadores: List[Notificador], logger: RegistroEvento) -> None:
        self._sensores = sensores
        self._notificadores = notificadores
        self._logger = logger

    def evaluar_y_notificar(self) -> None:
        self._logger.registrar_evento("EVALUACIÓN INICIADA", "Comenzando a evaluar sensores...")
        # Ejercicio Sensor2
        for s in self._sensores:
            if s.en_alerta():
                msg = f"ALERTA: Sensor {s.id} en umbral (avg={s.promedio:.2f})"
                self._logger.registrar_evento("ALERTA ACTIVA", msg)
                for n in self._notificadores:
                    n.enviar(msg)
                    self._logger.registrar_evento("NOTIFICACIÓN ENVIADA", f"Notificación enviada para {s.id}")
            else:
                self._logger.registrar_evento("SIN ALERTA", f"Sensor {s.id} dentro de los límites.")


class PlantaIndustrial:
    def __init__(self, gestores: List[GestorAlertas]) -> None:
        self._gestores = gestores

    def agregar_gestor(self, gestor: GestorAlertas) -> None:
        self._gestores.append(gestor)

    def evaluar_sensores(self) -> None:
        print("\nInicia evaluación...")
        for gestor in self._gestores:
            gestor.evaluar_y_notificar()
        print("... Evaluación terminada")

class RegistroEvento:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RegistroEvento, cls).__new__(cls)
        return cls._instance
    
    def registrar_evento(self, evento: str, mensaje: str) -> None:
        """Registra un evento con fecha y hora actual."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {evento}: {mensaje}")



def main():
    logger = RegistroEvento()

    print("\nPRUEBA: Sensor de Temperatura")
    
    sensor_temp = SensorTemperatura(id="temperatura_01", umbral=80.0)
    gestor_temp = GestorAlertas(
        sensores=[sensor_temp],
        notificadores=[NotificadorEmail("temp@test.com")],
        logger=logger
    )
    
    sensor_temp.leer(75.0) 
    gestor_temp.evaluar_y_notificar()
    
    sensor_temp.leer(85.0)  
    gestor_temp.evaluar_y_notificar()

    print("\nPRUEBA: Sensor de Vibración")
    
    sensor_vibr = SensorVibracion(id="vibracion_02", rms_umbral=2.5)
    gestor_vibr = GestorAlertas(
        sensores=[sensor_vibr],
        notificadores=[NotificadorWebhook("http://testVibracion.com")],
        logger=logger
    )
    
    sensor_vibr.leer(1.5) 
    gestor_vibr.evaluar_y_notificar()
    
    sensor_vibr.leer(3.0)
    gestor_vibr.evaluar_y_notificar()

    print("\nPRUEBA: Sensor de Humedad")
    
    sensor_hum = SensorHumedad(id="humedad_04", humedad_max=70.0)
    gestor_hum = GestorAlertas(
        sensores=[sensor_hum],
        notificadores=[NotificadorEmail("humedad@test.com")],
        logger=logger
    )
    
    sensor_hum.leer(65.0) 
    gestor_hum.evaluar_y_notificar()

    sensor_hum.leer(75.0)
    gestor_hum.evaluar_y_notificar()
    


if __name__ == "__main__":
    main()

    
