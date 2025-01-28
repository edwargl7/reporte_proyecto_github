import requests
import json
#import ollama
import xlsxwriter
from bs4 import BeautifulSoup


# Configuración de la API de Ollama
MODEL_NAME = "deepseek-r1:14b"  # Reemplaza con el nombre correcto del modelo en Ollama
PROMPT = "Resume la discusión de la issue en el siguiente enlace, destacando los problemas identificados, las soluciones propuestas y los avances logrados. Limita el resumen a 50 palabras y enfócate en los aspectos clave:"

# URL del proyecto
URL = "https://github.com/orgs/udistrital/projects/62"
Sprint_list=[]
Avance_list=[]

def obtener_issues_por_milestone(url):
    # Realizar la solicitud GET a la URL
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error al acceder a la página: {response.status_code}")
        return

    # Parsear el contenido HTML
    #print(response.text)

    with open('html-github.html', "w", encoding="utf-8") as f:
        f.write(response.text)
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # # Diccionario para almacenar los hitos y sus respectivas issues
    hitos = {}

    # # Buscar las secciones de milestone
    issues_text = soup.select_one('script[id="memex-items-data"]').text
    columns_text = soup.select_one('script[id="memex-columns-data"]').text
    #print(milestone_sections)
    issues=json.loads(issues_text)
    columns=json.loads(columns_text)
    #print(jsondata)
    # with open('data.json', "w", encoding="utf-8") as f:
    #     f.write(issues_text)
    #     f.write(columns_text)
    global Sprint_list
    Sprint_list= columns[13]["settings"]["configuration"]["completedIterations"]
    global Avance_list
    Avance_list= columns[16]["settings"]["options"]
    #print("sprint list",Sprint_list)

    for issue in issues:
        #print(issue)
        #print(issue["memexProjectColumnValues"][4])
        if issue["memexProjectColumnValues"][4]["value"]==None:
            continue
        title_mileston=issue["memexProjectColumnValues"][4]["value"]["title"]
        issue_format={
            "Sprint": setSpring(issue["memexProjectColumnValues"][7]["value"]["id"]),
            "Título": issue["memexProjectColumnValues"][0]["value"]["title"]["raw"],
            #"Descripción": generar_respuesta(issue["content"]["url"]),
            "Descripción":PROMPT+url,
            "Avance":setAvance(issue["memexProjectColumnValues"][10]["value"]),
            "URL": issue["content"]["url"],
        }
        #print(issue_format)
        if  title_mileston in hitos:
            hitos.get(title_mileston).append(issue_format)
        else:
            hitos[title_mileston]=[issue_format]

    # print(hitos.keys())
    # for hito in hitos:
    #     print(len(hito))
    
    create_excel_from_dict("issues_por_milestone.xlsx",hitos)
   
def setSpring(value):

    for sprint in Sprint_list:
        if sprint["id"]==value:
            return sprint["title"].split(" ")[1]

def setAvance(value):
    if value is not None:
        for avance in Avance_list:
            if avance["id"]==value["id"]:
                return avance["name"]
    else:
        return ""

def create_excel_from_dict(file_name, data):
    """
    Create an Excel file with sheets based on a dictionary.

    :param file_name: Name of the Excel file to create.
    :param data: Dictionary where keys are sheet names and values are lists of lists representing the sheet content.
    """
    # Create a new Excel file
    workbook = xlsxwriter.Workbook(file_name)

    for sheet_name, content in data.items():
        # Add a new worksheet for each key
        worksheet = workbook.add_worksheet(sheet_name[:31])  # Excel sheet names have a max length of 31 characters

       # Write the headers
        headers = ["Sprint", "Título", "Descripción","Avance", "URL"]
        for col_idx, header in enumerate(headers):
            worksheet.write(0, col_idx, header)

        # Write the content
        for row_idx, item in enumerate(content, start=1):
            worksheet.write(row_idx, 0, item.get("Sprint", ""))
            worksheet.write(row_idx, 1, item.get("Título", ""))
            worksheet.write(row_idx, 2, item.get("Descripción", ""))
            worksheet.write(row_idx, 3, item.get("Avance", ""))
            worksheet.write(row_idx, 4, item.get("URL", ""))

    # Close the workbook to save the file
    workbook.close()
        
# def generar_respuesta(url):
#     # Configura el payload para la solicitud
#     payload = [{
#         "role":"user",
#         "content": PROMPT+url,
#     },
#     ]

#     # Realiza la solicitud POST a la API de Ollama
#     response = ollama.chat(model=MODEL_NAME,messages=payload)
#     print(response)
#     # Verifica si la solicitud fue exitosa
#     # if response.status_code == 200:
#     #     print(response)
#     #     return response.json().get("response", "No se recibió respuesta")
#     # else:
#     #     return f"Error: {response.status_code}, {response.text}"

if __name__ == "__main__":
    obtener_issues_por_milestone(URL)