import sqlite3
from rich.console import Console
from rich.table import Table

console = Console()

# Имя файла базы данных
DB_FILE = "lists_data.db"


def init_db():
    """Инициализация базы данных."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Создание таблиц
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            list_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            debt TEXT NOT NULL,
            FOREIGN KEY (list_id) REFERENCES lists (id)
        )
    """)
    conn.commit()
    conn.close()


def get_all_lists():
    """Получение всех списков из базы данных."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM lists")
    lists = cursor.fetchall()
    conn.close()
    return lists


def create_list(list_name):
    """Создание нового списка."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO lists (name) VALUES (?)", (list_name,))
        conn.commit()
        console.print(f"[bold green]Список '{list_name}' создан.[/bold green]")
    except sqlite3.IntegrityError:
        console.print("[bold yellow]Список с таким именем уже существует.[/bold yellow]")
    conn.close()


def delete_list(list_id):
    """Удаление списка и всех его элементов."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM people WHERE list_id = ?", (list_id,))
    cursor.execute("DELETE FROM lists WHERE id = ?", (list_id,))
    conn.commit()
    conn.close()
    console.print("[bold green]Список удален.[/bold green]")


def get_people_from_list(list_id):
    """Получение людей из конкретного списка."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, surname, debt FROM people WHERE list_id = ?", (list_id,))
    people = cursor.fetchall()
    conn.close()
    return people


def add_person(list_id, name, surname, debt):
    """Добавление человека в список."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO people (list_id, name, surname, debt) VALUES (?, ?, ?, ?)",
                   (list_id, name, surname, debt))
    conn.commit()
    conn.close()
    console.print(f"[bold green]{name} {surname} добавлен в список.[/bold green]")


def delete_person(person_id):
    """Удаление человека из списка."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM people WHERE id = ?", (person_id,))
    conn.commit()
    conn.close()
    console.print("[bold green]Человек удален.[/bold green]")


def edit_person(person_id, new_name=None, new_surname=None, new_debt=None):
    """Редактирование информации о человеке."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if new_name:
        cursor.execute("UPDATE people SET name = ? WHERE id = ?", (new_name, person_id))
    if new_surname:
        cursor.execute("UPDATE people SET surname = ? WHERE id = ?", (new_surname, person_id))
    if new_debt:
        cursor.execute("UPDATE people SET debt = ? WHERE id = ?", (new_debt, person_id))
    conn.commit()
    conn.close()
    console.print("[bold green]Изменения сохранены.[/bold green]")


def show_people(people):
    """Отображение списка людей."""
    if not people:
        console.print("[bold red]Список пуст.[/bold red]")
    else:
        table = Table(title="Список людей", show_header=True, header_style="bold blue")
        table.add_column("№", justify="center", style="cyan", width=4)
        table.add_column("Имя", style="green")
        table.add_column("Фамилия", style="magenta")
        table.add_column("Долг", justify="right", style="red")

        for i, person in enumerate(people, start=1):
            table.add_row(str(i), person[1], person[2], person[3])

        console.print(table)


def manage_list(list_id, list_name):
    """Управление конкретным списком."""
    console.print(f"\n[bold blue]Управление списком: {list_name}[/bold blue]")
    while True:
        console.print("\n1. [green]Показать людей[/green]")
        console.print("2. [green]Добавить человека[/green]")
        console.print("3. [green]Редактировать человека[/green]")
        console.print("4. [green]Удалить человека[/green]")
        console.print("5. [green]Вернуться в главное меню[/green]")

        choice = console.input("[bold cyan]Выберите действие: [/bold cyan]")

        if choice == "1":
            people = get_people_from_list(list_id)
            show_people(people)
        elif choice == "2":
            name = console.input("[cyan]Введите имя: [/cyan]")
            surname = console.input("[cyan]Введите фамилию: [/cyan]")
            debt = console.input("[cyan]Введите долг: [/cyan]")
            add_person(list_id, name, surname, debt)
        elif choice == "3":
            people = get_people_from_list(list_id)
            show_people(people)
            person_id = int(console.input("[cyan]Введите номер человека для редактирования: [/cyan]"))
            new_name = console.input("[cyan]Новое имя (оставьте пустым для пропуска): [/cyan]")
            new_surname = console.input("[cyan]Новая фамилия (оставьте пустым для пропуска): [/cyan]")
            new_debt = console.input("[cyan]Новый долг (оставьте пустым для пропуска): [/cyan]")
            edit_person(person_id, new_name, new_surname, new_debt)
        elif choice == "4":
            people = get_people_from_list(list_id)
            show_people(people)
            person_id = int(console.input("[cyan]Введите номер человека для удаления: [/cyan]"))
            delete_person(person_id)
        elif choice == "5":
            break
        else:
            console.print("[bold red]Неверный выбор, попробуйте снова.[/bold red]")


def main():
    init_db()
    while True:
        console.print("\n[bold blue]Главное меню:[/bold blue]")
        console.print("1. [green]Создать новый список[/green]")
        console.print("2. [green]Выбрать список[/green]")
        console.print("3. [green]Удалить список[/green]")
        console.print("4. [green]Выйти[/green]")

        choice = console.input("[bold cyan]Выберите действие: [/bold cyan]")

        if choice == "1":
            list_name = console.input("[cyan]Введите имя нового списка: [/cyan]")
            create_list(list_name)
        elif choice == "2":
            lists = get_all_lists()
            if not lists:
                console.print("[bold red]Нет доступных списков.[/bold red]")
                continue

            console.print("\n[bold blue]Доступные списки:[/bold blue]")
            for i, (list_id, list_name) in enumerate(lists, start=1):
                console.print(f"{i}. {list_name}")

            try:
                index = int(console.input("[cyan]Введите номер списка: [/cyan]")) - 1
                if 0 <= index < len(lists):
                    list_id, list_name = lists[index]
                    manage_list(list_id, list_name)
                else:
                    console.print("[bold red]Неверный выбор, попробуйте снова.[/bold red]")
            except ValueError:
                console.print("[bold red]Ошибка: Введите число![/bold red]")
        elif choice == "3":
            lists = get_all_lists()
            if not lists:
                console.print("[bold red]Нет доступных списков.[/bold red]")
                continue

            console.print("\n[bold blue]Доступные списки:[/bold blue]")
            for i, (list_id, list_name) in enumerate(lists, start=1):
                console.print(f"{i}. {list_name}")

            try:
                index = int(console.input("[cyan]Введите номер списка для удаления: [/cyan]")) - 1
                if 0 <= index < len(lists):
                    list_id, list_name = lists[index]
                    delete_list(list_id)
                else:
                    console.print("[bold red]Неверный выбор, попробуйте снова.[/bold red]")
            except ValueError:
                console.print("[bold red]Ошибка: Введите число![/bold red]")
        elif choice == "4":
            console.print("[bold green]Выход из программы.[/bold green]")
            break
        else:
            console.print("[bold red]Неверный выбор, попробуйте снова.[/bold red]")


if __name__ == "__main__":
    main()
