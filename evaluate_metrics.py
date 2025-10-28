
import re

def evaluar_exactitud(respuesta, respuesta_esperada):
    """Compara si la respuesta generada coincide exactamente con la esperada (binario)."""
    return int(respuesta.strip().lower() == respuesta_esperada.strip().lower())

def evaluar_cobertura(respuesta, conceptos_clave):
    """Evalúa cuántos conceptos clave aparecen en la respuesta (escala de 0.0 a 1.0)."""
    if not conceptos_clave:
        return 0
    count = sum(1 for c in conceptos_clave if c.lower() in respuesta.lower())
    return round(count / len(conceptos_clave), 2)

def evaluar_claridad(respuesta):
    """Evalúa claridad basada en la longitud de la respuesta (escala simulada de 1 a 5)."""
    longitud = len(respuesta.strip().split())
    if longitud < 5:
        return 1
    elif longitud < 15:
        return 2
    elif longitud < 30:
        return 3
    elif longitud < 50:
        return 4
    else:
        return 5

def detectar_alucinacion(respuesta):
    """Detecta si la respuesta probablemente alucina (no usa frases de seguridad)."""
    frases_seguras = ["no tengo información", "no dispongo", "no sé", "no se puede confirmar"]
    for frase in frases_seguras:
        if frase in respuesta.lower():
            return 0
    return 1

def detectar_cita_valida(respuesta):
    """Detecta si hay una cita válida (URL o mención de fuente confiable)."""
    url_pattern = r"https?://[^\s]+"
    fuente_claves = ["unesco", "ocde", "ieee", "ai act", "libro", "manual", "artículo", "doi", "fuente:"]
    if re.search(url_pattern, respuesta):
        return 1
    for fuente in fuente_claves:
        if fuente in respuesta.lower():
            return 1
    return 0
