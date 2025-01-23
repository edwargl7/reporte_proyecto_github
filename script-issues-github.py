import csv
import re
from github import Github

# Token de acceso personal
TOKEN = 'TOKEN'

REPO_NAME = 'udistrital/polux_cliente'

# Crear una instancia de la clase Github autenticada
g = Github(TOKEN)

pattern = r'\(https:\/\/github\.com\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+(?:\/[a-zA-Z0-9_-]+)*\)'

def issue_2_dict(issue, description, milestone) -> dict:
    assignees = [assignee.login for assignee in issue.assignees]
    assignees_str = ','.join(assignees if assignees else "Ninguno")
    return {
        "Número": issue.number,
        "Título": issue.title,
        "Descripción": description.replace("\n", " "),  # Eliminar saltos de línea
        "Milestone": milestone,
        "URL": issue.html_url,
        "Fecha de Creación": issue.created_at.strftime("%Y-%m-%d"),
        "Asignados": assignees_str
    }

def split_issue_body(issue_body: str, split_2: list, chosen_part: int = 0) -> str:
    if not issue_body:  
        return ""

    if not split_2:
        split_2 = ["**Sub Tareas**", "**Subtareas**"]
    
    for sp in split_2:
        issue_body = issue_body.split(sp)[chosen_part]
    
    return issue_body

def clear_issue(issue_body: str) -> str:
    description = re.sub(pattern, '', issue_body)
    description = description.replace("[", "").replace("]", "").replace("!image", "")
    description = re.sub(r'\n+', '\n', description)
    return description

def get_issues_by_range_date():
    try:
        fecha_inicio = "2024-04-29"
        fecha_fin = "2025-01-23"

        repo = g.get_repo(REPO_NAME)

        query = f"repo:{REPO_NAME} created:{fecha_inicio}..{fecha_fin}"
        issues = sorted(g.search_issues(query), key=lambda issue: issue.created_at)

        issues_list = []

        for issue in issues:
            print(f"Procesando Issue {issue.number} ...")
            issue_body = issue.body if issue.body else ""
            description = split_issue_body(issue_body, [])
            description = clear_issue(description)
            milestone_name = issue.milestone.title if issue.milestone else "Sin Milestone"
            issues_list.append(issue_2_dict(issue, description, milestone_name))

        # Guardar en CSV con punto y coma como delimitador
        with open("issues_por_milestone.csv", "w", encoding="utf-8-sig", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Número", "Título", "Descripción", "Milestone", "URL", "Fecha de Creación", "Asignados"], delimiter=';', quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(issues_list)

        print("¡Proceso completado! Se ha generado issues_por_milestone.csv con formato mejorado.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    get_issues_by_range_date()
