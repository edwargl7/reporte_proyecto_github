import re

from github import Github

# Token de acceso personal
TOKEN = 'TOKEN'

# Nombre del repositorio en formato 'usuario/repositorio'
REPO_NAME = 'X/Y'

# Crear una instancia de la clase Github autenticada
g = Github(TOKEN)

pattern = r'\(https:\/\/github\.com\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+(?:\/[a-zA-Z0-9_-]+)*\)'


def issue_2_info_dict(issue, description) -> dict:
    issue_summary = {
        "number": issue.number,
        "URL": issue.html_url,
        "title": issue.title,
        "description": description
    }
    return issue_summary


def issue_2_dict(issue, description) -> dict:
    issue_summary = {
        "number": issue.number,
        "title": issue.title,
        "description": description
    }
    return issue_summary


def issue_2_info_text(issue, description) -> str:
    text = f"Número: {issue.number}\n"
    text += f"URL: {issue.html_url}\n"
    text += f"Título: {issue.title}\n"
    text += f"Descripción: {description}\n"
    return text


def issue_2_text(issue, description) -> str:
    text = f"Número: {issue.number}\n"
    text += f"Título: {issue.title}\n"
    text += f"Descripción: {description}\n"
    return text


def split_issue_body(issue_body: str, split_2: list, chosen_part: int = 0) -> str:
    if not issue_body:  # Manejo del caso donde el body es None
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
        # Define el rango de fechas en formato ISO 8601 (YYYY-MM-DD)
        fecha_inicio = "2024-04-29"
        fecha_fin = "2025-01-23"

        # El autor a excluir
        autor_excluir = "USUARIO-GTIHUB"

        repo = g.get_repo(REPO_NAME)

        # Realiza la búsqueda de issues por rango de fechas en el repositorio excluyendo un autor
        query = f"repo:{REPO_NAME} created:{fecha_inicio}..{fecha_fin}"
        issues = sorted(g.search_issues(query), key=lambda issue: issue.created_at)

        issues_by_milestone = {}

        for issue in issues:
            print(f"Issue {issue.number} ...")
            issue_body = issue.body if issue.body else ""
            description = split_issue_body(issue_body, [])
            description = clear_issue(description)

            milestone_name = issue.milestone.title if issue.milestone else "Sin Milestone"

            if milestone_name not in issues_by_milestone:
                issues_by_milestone[milestone_name] = []

            issues_by_milestone[milestone_name].append(issue_2_text(issue, description))

        with open("issues_por_milestone.txt", "w", encoding="utf-8") as f:
            for milestone, issues_list in issues_by_milestone.items():
                f.write(f"==== Milestone: {milestone} ====\n\n")
                for issue_text in issues_list:
                    f.write(issue_text + "\n")
                f.write("\n")  # Espacio entre milestones

        print("¡Proceso completado! Las issues se han organizado por milestone.")
    except Exception as e:
        print(f"Error: {e}")


def get_issues_by_numbers():
    try:
        # Obtener el repositorio
        repo = g.get_repo(REPO_NAME)
        print("REPO OK")
        issues_ids = [97, 91, 100, 99, 98]
        issues_ids += [103, 102, 78, 104, 101, 105]
        issues_ids += [83, 108, 109, 110, 111, 112]
        issues_ids += [114, 117, 118, 119, 116, 115, 121]
        issues_ids += []

        # Obtener todas las Issues
        for issue_id in issues_ids:
            issue = repo.get_issue(number=issue_id)
            print(f"Issue {issue_id} ...")
            description = split_issue_body(issue.body, [])
            description = clear_issue(description)

            with open("issues.txt", "a") as f:
                f.write(issue_2_text(issue, description))
                f.write("\n")
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    # get_issues_by_numbers()
    get_issues_by_range_date()

