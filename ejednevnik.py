import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import date

DATA_FILE = "tasks.json"


class PlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Мой ежедневник")
        self.root.geometry("300x600")

        self.tasks = []  # список словарей: {"text": ..., "done": ...}
        self.load_tasks()

        # Заголовок с датой
        today = date.today().strftime("%d.%m.%Y")
        tk.Label(root, text=f"Планы на {today}", font=("Arial", 14, "bold")).pack(pady=10)

        # Поле ввода + кнопка
        input_frame = tk.Frame(root)
        input_frame.pack(fill="x", padx=10)

        self.entry = tk.Entry(input_frame, font=("Arial", 12))
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry.bind("<Return>", lambda e: self.add_task())

        tk.Button(input_frame, text="Добавить", command=self.add_task).pack(side="left")

        # Область со списком задач (прокручиваемая)
        list_frame = tk.Frame(root)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(list_frame, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.tasks_frame = tk.Frame(self.canvas)

        self.tasks_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.tasks_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопка очистки выполненных
        tk.Button(root, text="Удалить выполненные", command=self.clear_done).pack(pady=5)

        self.refresh_list()

    # ---------- Работа с данными ----------
    def load_tasks(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
            except Exception:
                self.tasks = []

    def save_tasks(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    # ---------- Действия ----------
    def add_task(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.tasks.append({"text": text, "done": False})
        self.entry.delete(0, tk.END)
        self.save_tasks()
        self.refresh_list()

    def toggle_task(self, index):
        self.tasks[index]["done"] = not self.tasks[index]["done"]
        self.save_tasks()
        self.refresh_list()

    def delete_task(self, index):
        if messagebox.askyesno("Удаление", "Удалить эту задачу?"):
            del self.tasks[index]
            self.save_tasks()
            self.refresh_list()

    def clear_done(self):
        if not any(t["done"] for t in self.tasks):
            return
        if messagebox.askyesno("Очистка", "Удалить все выполненные задачи?"):
            self.tasks = [t for t in self.tasks if not t["done"]]
            self.save_tasks()
            self.refresh_list()

    # ---------- Отрисовка ----------
    def refresh_list(self):
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()

        if not self.tasks:
            tk.Label(self.tasks_frame, text="Пока нет планов. Добавьте первый!",
                     fg="gray", font=("Arial", 11)).pack(pady=20)
            return

        for i, task in enumerate(self.tasks):
            row = tk.Frame(self.tasks_frame)
            row.pack(fill="x", pady=2)

            var = tk.BooleanVar(value=task["done"])

            chk = tk.Checkbutton(
                row, variable=var,
                command=lambda i=i: self.toggle_task(i)
            )
            chk.pack(side="left")

            font_style = ("Arial", 12, "overstrike") if task["done"] else ("Arial", 12)
            color = "gray" if task["done"] else "black"

            lbl = tk.Label(row, text=task["text"], font=font_style, fg=color,
                           anchor="w", justify="left")
            lbl.pack(side="left", fill="x", expand=True, padx=5)

            del_btn = tk.Button(row, text="✕", fg="red", bd=0,
                                command=lambda i=i: self.delete_task(i))
            del_btn.pack(side="right")


if __name__ == "__main__":
    root = tk.Tk()
    app = PlannerApp(root)
    root.mainloop()