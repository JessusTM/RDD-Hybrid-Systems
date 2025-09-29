# istar_uvl_with_clean_labels.py
# Uso: python3 istar_uvl_with_clean_labels.py Chemistry.xml modelo.uvl

import sys
import re
import html
import unicodedata
import xml.etree.ElementTree as ET

def cleanLabelText(rawText: str) -> str:
    """
    Limpia un texto proveniente de draw.io:
    - Decodifica entidades HTML (&nbsp; -> espacio).
    - Elimina etiquetas HTML (<div>, <br>, etc.).
    - Devuelve texto plano listo para normalizar.

    Args:
        rawText (str): Texto original del nodo i*.
    Returns:
        str: Texto limpio sin HTML ni entidades.
    """
    if rawText is None:
        return ""
    decoded = html.unescape(rawText)
    withoutTags = re.sub(r"<[^>]+>", " ", decoded)
    return withoutTags.strip()

def normalizeText(inputText: str) -> str:
    """
    Convierte un texto a minúsculas, elimina acentos y espacios extra.

    Args:
        inputText (str): Texto a normalizar.
    Returns:
        str: Texto en minúsculas, sin acentos ni espacios extra.
    """
    if inputText is None:
        return ""
    lowerCaseText = inputText.strip().lower()
    decomposedText = unicodedata.normalize("NFD", lowerCaseText)
    charactersWithoutAccents = []
    for character in decomposedText:
        if unicodedata.category(character) != "Mn":
            charactersWithoutAccents.append(character)
    textWithoutAccents = "".join(charactersWithoutAccents)
    cleanedText = " ".join(textWithoutAccents.split())
    return cleanedText

def convertTextToUvlIdentifier(inputText: str) -> str:
    """
    Convierte texto libre en un identificador válido de UVL en CamelCase.

    Args:
        inputText (str): Texto original.
    Returns:
        str: Identificador válido en CamelCase.
    """
    if inputText is None:
        return "RootGoal"
    cleanedCharacters = []
    for character in inputText:
        if character.isalnum() or character in (" ", "_"):
            cleanedCharacters.append(character)
        else:
            cleanedCharacters.append(" ")
    joinedText = "".join(cleanedCharacters)
    separatedText = joinedText.replace("_", " ")
    splitWords = separatedText.split()
    words = []
    for word in splitWords:
        if word.isalnum():
            capitalizedWord = word.capitalize()
            words.append(capitalizedWord)
    if len(words) == 0:
        return "RootGoal"
    else:
        finalIdentifier = "".join(words)
        return finalIdentifier

def loadMappingFile(filePath: str) -> dict:
    """
    Lee un archivo de mapeo clave => Feature y devuelve un diccionario normalizado.

    Args:
        filePath (str): Ruta al archivo de configuración.
    Returns:
        dict: Diccionario de mapeo {clave normalizada: feature}.
    """
    mappingDictionary = {}
    try:
        with open(filePath, encoding="utf-8") as file:
            for line in file:
                cleanedLine = line.strip()
                if not cleanedLine or cleanedLine.startswith("#") or "=>" not in cleanedLine:
                    continue
                keyPart, featurePart = line.split("=>", 1)
                normalizedKey = normalizeText(keyPart)
                mappingDictionary[normalizedKey] = featurePart.strip()
    except FileNotFoundError:
        pass
    return mappingDictionary

def loadAllMappingFiles(configDirectory: str) -> dict:
    """
    Carga los diccionarios de algoritmos, NFRs, backend e integración desde config/.

    Args:
        configDirectory (str): Carpeta con los archivos de configuración.
    Returns:
        dict: Diccionarios de mapeo organizados por categoría.
    """
    allMappings = {}
    allMappings["algorithms"] = loadMappingFile(f"{configDirectory}/algorithms.txt")
    allMappings["nfrs"] = loadMappingFile(f"{configDirectory}/nfrs.txt")
    allMappings["backend"] = loadMappingFile(f"{configDirectory}/backend.txt")
    allMappings["integration"] = loadMappingFile(f"{configDirectory}/integration.txt")
    return allMappings

def parseIStarXml(xmlFilePath: str) -> list:
    """
    Lee un archivo XML de i* y devuelve lista de objetos con type, label y norm.

    Args:
        xmlFilePath (str): Ruta al archivo XML de entrada.
    Returns:
        list: Lista de diccionarios con atributos de cada objeto.
    """
    parsedObjects = []
    root = ET.parse(xmlFilePath).getroot()
    for obj in root.findall(".//object"):
        rawLabel = obj.get("label") or ""
        labelText = cleanLabelText(rawLabel)
        typeText = (obj.get("type") or "").lower()
        normalizedLabel = normalizeText(labelText)
        parsedObjects.append({
            "type": typeText,
            "label": labelText,
            "norm": normalizedLabel
        })
    return parsedObjects

def mapIStarObjectsToFeatures(objectList: list, mappingDictionaries: dict):
    """
    Mapea objetos i* a algoritmos, NFRs, backends e integraciones.

    Args:
        objectList (list): Objetos extraídos del XML.
        mappingDictionaries (dict): Diccionarios de mapeo.
    Returns:
        tuple: Listas de algoritmos, NFRs, backends e integraciones.
    """
    algos = set()
    nfrs = set()
    backs = set()
    integrs = set()
    for obj in objectList:
        txt = obj["norm"]
        for keyword, feature in mappingDictionaries["algorithms"].items():
            if keyword in txt:
                algos.add(feature)
        for keyword, feature in mappingDictionaries["nfrs"].items():
            if keyword in txt:
                nfrs.add(feature)
        for keyword, feature in mappingDictionaries["backend"].items():
            if keyword in txt:
                backs.add(feature)
        for keyword, feature in mappingDictionaries["integration"].items():
            if keyword in txt:
                integrs.add(feature)
    backs, integrs = applyDefaultValues(backs, integrs, mappingDictionaries)
    return sorted(algos), sorted(nfrs), sorted(backs), sorted(integrs)

def applyDefaultValues(backs: set, integrs: set, mappingDictionaries: dict):
    """
    Agrega valores por defecto a backend e integración si no se detectaron.

    Args:
        backs (set): Conjunto de backends detectados.
        integrs (set): Conjunto de integraciones detectadas.
        mappingDictionaries (dict): Diccionarios de mapeo.
    Returns:
        tuple: Conjuntos actualizados de backends e integraciones.
    """
    backendValues = mappingDictionaries["backend"].values()
    integrationValues = mappingDictionaries["integration"].values()
    if len(backs) == 0 and "Hardware" in backendValues:
        backs.add("Hardware")
    if len(integrs) == 0 and "Middleware" in integrationValues:
        integrs.add("Middleware")
    return backs, integrs

def buildUvlModel(rootFeature: str, algos: list, nfrs: list, backs: list, integrs: list) -> str:
    """
    Construye el modelo UVL como texto a partir de features detectadas.

    Args:
        rootFeature (str): Feature raíz del modelo.
        algos (list): Algoritmos detectados.
        nfrs (list): NFRs detectados.
        backs (list): Backends detectados.
        integrs (list): Integraciones detectadas.
    Returns:
        str: Modelo UVL en formato de texto.
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
    Ejecuta todo el proceso: carga mappings, parsea XML, construye UVL y lo guarda.

    Args:
        inputXmlFile (str): Archivo XML de entrada.
        outputUvlFile (str): Archivo UVL de salida.
        configDirectory (str): Carpeta con archivos de mapeo.
    """
    mappingDictionaries = loadAllMappingFiles(configDirectory)
    objectList = parseIStarXml(inputXmlFile)
    rootLabel = "Protein Folding"
    for obj in objectList:
        if obj["type"] == "goal" and obj["label"].strip() != "":
            rootLabel = obj["label"]
            break
    rootFeature = convertTextToUvlIdentifier(rootLabel)
    algos, nfrs, backs, integrs = mapIStarObjectsToFeatures(objectList, mappingDictionaries)
    uvlContent = buildUvlModel(rootFeature, algos, nfrs, backs, integrs)
    with open(outputUvlFile, "w", encoding="utf-8") as outputFile:
        outputFile.write(uvlContent)
    print(f"UVL generado en {outputUvlFile}")

if __name__ == "__main__":
    inputXmlFile = sys.argv[1] if len(sys.argv) > 1 else "Chemistry.xml"
    outputUvlFile = sys.argv[2] if len(sys.argv) > 2 else "modelo.uvl"
    generateUvlFromIStarXml(inputXmlFile, outputUvlFile, "config")

