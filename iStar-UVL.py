import sys
import re
import html
from unidecode import unidecode
from lxml import etree

def cleanLabelText(rawText: str) -> str:
    """
    Decodifica HTML y elimina etiquetas, devolviendo solo texto plano.

    Args:
        rawText (str): Texto con posibles entidades o etiquetas HTML.

    Returns:
        str: Texto limpio sin HTML. Si es None, devuelve "".
    """
    if rawText is None : return ""
    decoded     = html.unescape(rawText)
    withoutTags = re.sub(r"<[^>]+>", " ", decoded).strip()
    return withoutTags





def normalizeText(inputText: str) -> str:
    """
    Convierte un texto a minúsculas, elimina acentos y espacios extra.

    Args:
        inputText (str): Texto a normalizar.

    Returns:
        str: Texto en minúsculas, sin acentos ni espacios duplicados. 
             Si es None, devuelve "".
    """
    if inputText is None : return ""
    lowerCaseText       = inputText.strip().lower()
    textWithoutAccents  = unidecode(lowerCaseText)
    words               = textWithoutAccents.split()
    cleanedText         = " ".join(words)
    return cleanedText





def formatRootFeatureName(inputText: str) -> str:
    """
    Genera el nombre de la feature raíz en formato PascalCase.

    Elimina HTML, normaliza acentos y espacios, y capitaliza cada palabra.
    Si el texto es inválido o vacío, devuelve "RootGoal".

    Args:
        inputText (str): Texto original del label raíz en i*.

    Returns:
        str: Nombre de la feature raíz en PascalCase para usar en UVL.
    """
    if not inputText:
        return "RootGoal"

    cleaned          = cleanLabelText(inputText)
    normalized       = normalizeText(cleaned)
    words            = normalized.replace("_", " ").split()
    capitalizedWords = []

    for word in words:
        if word.isalnum():
            capitalizedWords.append(word.capitalize())

    identifier = "".join(capitalizedWords)
    return identifier or "RootGoal"






def loadMappingFile(filePath: str) -> dict:
    """
    Carga un diccionario con formato clave => feature en el proyecto.

    Args:
        filePath (str): Ruta al archivo de configuración.

    Returns:
        dict: Diccionario con claves normalizadas y sus features asociadas.
    """
    mapping = {}
    
    with open(filePath, encoding="utf-8") as file:
        for line in file:
            cleanedLine = line.strip()

            if cleanedLine is None : continue
            if "=>" not in cleanedLine : continue
            
            keyPart, featurePart = cleanedLine.split("=>", 1)
            normalizedKey = normalizeText(keyPart)
            normalizedFeature = featurePart.strip()
            mapping[normalizedKey] = normalizedFeature
    return mapping





def loadAllMappingFiles(configDirectory: str) -> dict:
    """
    Carga todos los diccionarios (algorithms, nfrs, backend, integration).

    Args:
        configDirectory (str): Carpeta donde están los archivos de configuración.

    Returns:
        dict: Diccionario con los mapeos agrupados por categoría.
    """
    categories          = ["algorithms", "nfrs", "backend", "integration"]
    categoryMappings    = {}

    for category in categories:
        filePath        = f"{configDirectory}/{category}.txt"
        mapping         = loadMappingFile(filePath)
        categoryMappings[category] = mapping

    return categoryMappings





def parseIStarXml(xmlFilePath: str) -> list:
    """
    Parsea un archivo XML de i* a una estructura Python como diccionarios.

    Args:
        xml_file (str): Ruta al archivo XML de entrada.

    Returns:
        list: Lista de diccionarios con 'type', 'label' y 'norm'.
    """
    tree    = etree.parse(xmlFilePath)
    result  = []

    for obj in tree.xpath("//object"):
        rawLabel        = obj.get("label", "")
        label           = cleanLabelText(rawLabel)
        rawType         = obj.get("type", "")
        typeText        = rawType.lower() if rawType else ""
        normalizedLabel = normalizeText(label)
        objData         = {
            "type"  : typeText,
            "label" : label,
            "norm"  : normalizedLabel
        }
        result.append(objData)
    return result





def mapIStarObjectsToFeatures(objectList: list, mappingDictionaries: dict):
    """
    Asigna objetos i* a features UVL según los diccionarios de mapeo.

    Args:
        objectList (list)           : Objetos con 'norm' generado por parseIStarXml.
        mappingDictionaries (dict)  : Diccionarios de keywords por categoría.

    Returns:
        tuple: Listas ordenadas de algoritmos, NFRs, backends e integraciones.
    """
    algos   = set()
    nfrs    = set()
    backs   = set()
    integrs = set()
    for obj in objectList:
        txt = obj["norm"]
        for keyword, feature in mappingDictionaries["algorithms"].items():
            if keyword in txt : algos.add(feature)
        
        for keyword, feature in mappingDictionaries["nfrs"].items():
            if keyword in txt : nfrs.add(feature)
        
        for keyword, feature in mappingDictionaries["backend"].items():
            if keyword in txt : backs.add(feature)
        
        for keyword, feature in mappingDictionaries["integration"].items():
            if keyword in txt : integrs.add(feature)
    
    backs, integrs = applyDefaultValues(backs, integrs, mappingDictionaries)
    return sorted(algos), sorted(nfrs), sorted(backs), sorted(integrs)





def applyDefaultValues(backs: set, integrs: set, mappingDictionaries: dict):
    """
    Agrega valores por defecto a backend e integración si no hay detecciones.

    Args:
        backs (set)                 : Conjunto de backends encontrados.
        integrs (set)               : Conjunto de integraciones encontradas.
        mappingDictionaries (dict)  : Diccionarios de mapeo por categoría.

    Returns:
        tuple: Conjuntos actualizados de backends e integraciones.
    """
    backendValues       = mappingDictionaries["backend"].values()
    integrationValues   = mappingDictionaries["integration"].values()
    if len(backs) == 0 and "Hardware" in backendValues:
        backs.add("Hardware")
    if len(integrs) == 0 and "Middleware" in integrationValues:
        integrs.add("Middleware")
    return backs, integrs





def buildUvlModel(rootFeature: str, algos: list, nfrs: list, backs: list, integrs: list) -> str:
    """
    Construye el modelo UVL como texto a partir de las features detectadas.

    Args:
        rootFeature (str)   : Nombre de la feature raíz.
        algos (list)        : Algoritmos.
        nfrs (list)         : Requerimientos no funcionales.
        backs (list)        : Backends.
        integrs (list)      : Integraciones.

    Returns:
        str: Representación UVL en formato de texto.
    """
    lines = []
    lines.append("features {")
    lines.append(f"  {rootFeature} {{")
    if len(algos) > 0:
        lines.append("    Algorithm {")
        for algo in algos:
            lines.append(f"      {algo}")
        lines.append("    }")
    if len(backs) > 0:
        lines.append("    Backend {")
        for back in backs:
            lines.append(f"      {back}")
        lines.append("    }")
    if len(integrs) > 0:
        lines.append("    IntegrationModel {")
        for integr in integrs:
            lines.append(f"      {integr}")
        lines.append("    }")
    for n in nfrs:
        lines.append(f"    {n}")
    lines.append("  }")
    lines.append("}")
    lines.append("")
    if len(algos) > 0 and "Precision" in nfrs:
        lines.append("constraints {")
        for algo in algos:
            lines.append(f"  {algo} requires Precision")
        lines.append("}")
    return "\n".join(lines)





def generateUvlFromIStarXml(inputXmlFile: str, outputUvlFile: str, configDirectory: str = "config"):
    """
    Genera un modelo UVL a partir de un XML de i*.

    Carga los diccionarios de mapeo, parsea el XML, detecta el goal raíz,
    asigna features y construye el modelo UVL que se guarda en archivo.

    Args:
        inputXmlFile (str)              : Ruta al archivo XML de entrada (i*).
        outputUvlFile (str)             : Ruta al archivo UVL de salida.
        configDirectory (str, optional) : Carpeta con los archivos de mapeo.
    """
    mappingDictionaries = loadAllMappingFiles(configDirectory)
    objectList          = parseIStarXml(inputXmlFile)
    
    for obj in objectList:
        if obj["type"] == "goal" and obj["label"].strip() != "":
            rootLabel = obj["label"]
            break
  
    rootFeature = formatRootFeatureName(rootLabel)
    algos, nfrs, backs, integrs = mapIStarObjectsToFeatures(objectList, mappingDictionaries)
    uvlContent = buildUvlModel(rootFeature, algos, nfrs, backs, integrs)
    with open(outputUvlFile, "w", encoding="utf-8") as outputFile:
        outputFile.write(uvlContent)
    print(f"UVL generado en {outputUvlFile}")





if __name__ == "__main__":
    inputXmlFile = sys.argv[1] 
    outputUvlFile = sys.argv[2] 
    generateUvlFromIStarXml(inputXmlFile, outputUvlFile, "config")
