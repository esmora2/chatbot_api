import csv
import os

entrada = os.path.join("media", "docs", "basecsvf.csv")
salida = os.path.join("media", "docs", "basecsvf_backup.csv")

with open(entrada, encoding="utf-8") as infile, open(salida, mode="w", newline='', encoding="utf-8") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["id", "Pregunta", "Respuesta", "Categoría", "fechaCreacion", "fechaModificacion"])  # encabezado

    reader = csv.reader(infile)
    current_id = 1
    for row in reader:
        if len(row) < 2:
            continue  # saltar filas mal formateadas
        pregunta = row[0].strip()
        respuesta = row[1].strip()
        if pregunta.lower() == "pregunta":  # saltar encabezados repetidos
            continue
        writer.writerow([current_id, pregunta, respuesta, "", "", ""])
        current_id += 1
