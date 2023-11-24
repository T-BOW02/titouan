import json
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from PIL import Image, ImageTk
import datetime
import winsound
class TodoList:
    def __init__(self, name, time):
        self.name = name
        self.time = time
        self.tasks = []

    def add_task(self, task_name, task_image_path):
        task = {"name": task_name, "image_path": task_image_path, "checked": tk.BooleanVar()}
        self.tasks.append(task)

    def show_tasks(self):
        self.task_window = tk.Toplevel()
        self.task_window.title(f"{self.name} - {self.time}")
        self.task_window.overrideredirect(1)
        self.task_window.attributes('-topmost', True)

        screen_width, screen_height = self.task_window.winfo_screenwidth(), self.task_window.winfo_screenheight()
        window_width, window_height = screen_width // 5, (screen_height * 3) // 4  # Adjust window height
        x_position = screen_width - window_width
        y_position = (screen_height - window_height) // 2
        geometry_string = f"{window_width}x{window_height}+{x_position}+{y_position}"
        self.task_window.geometry(geometry_string)

        # Displaying the time at the top of the window
        time_label = tk.Label(self.task_window, text=self.time, font=("Arial", 48))
        time_label.pack(anchor='n', pady=20)  # Centered horizontally, with padding from the top
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        for task in self.tasks:
            task_frame = tk.Frame(self.task_window, bd=1, relief='solid')  # Add border for visualization
            task_frame.pack(fill=tk.BOTH, expand=True, anchor='ne')
            task['checked'].set(False)  # Ensure the check button is unchecked


            task_image = Image.open(task['image_path'])
            task_image = task_image.resize((100, 100), Image.LANCZOS)
            task_photo = ImageTk.PhotoImage(task_image)

            task_label = tk.Label(task_frame, image=task_photo)
            task_label.photo = task_photo
            task_label.pack(side=tk.LEFT)

            task_info_label = tk.Label(task_frame, text=f"{task['name']}", font=("Arial", 24))
            task_info_label.pack(side=tk.LEFT)

            check_button = tk.Checkbutton(task_frame, variable=task['checked'], command=self.check_all_tasks)
            check_button.pack(side=tk.RIGHT)

            self.task_window.after(600000, self.auto_close_window)#10min
    def check_all_tasks(self):
        if all(task['checked'].get() for task in self.tasks):  # Modifiez cette ligne
            self.task_window.destroy()

    def auto_close_window(self):
        if not all(task['checked'].get() for task in self.tasks):
            self.task_window.destroy()

class TodoListManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Titouan")
        self.root.geometry("400x400")
        self.todo_lists = []

        self.list_frame = tk.Frame(root)
        self.list_frame.pack(fill=tk.BOTH, expand=False)

        self.add_list_button = tk.Button(root, text="Ajouter une liste", command=self.add_list)
        self.add_list_button.pack()

        self.load_data()
        self.check_time()

    def check_time(self):
        now = datetime.datetime.now().strftime('%H:%M')
        for todo_list in self.todo_lists:
            if todo_list.time == now and not hasattr(todo_list, 'task_window'):
                todo_list.show_tasks()
                self.root.after(60000, todo_list.check_all_tasks)  # Check again in 1 minute
        self.root.after(60000, self.check_time)
    def add_list(self):
        list_name = simpledialog.askstring("Input", "Entrez le nom de la liste:")
        if not list_name:
            messagebox.showerror("Erreur", "Le nom de la liste est requis!")
            return

        list_time = simpledialog.askstring("Input", "Entrez l'heure à laquelle la liste doit être effectuée (HH:MM):")
        if not list_time:
            messagebox.showerror("Erreur", "L'heure de la liste est requise!")
            return

        todo_list = TodoList(list_name, list_time)
        self.todo_lists.append(todo_list)
        self.display_list(todo_list)
        self.save_data()

    def add_task(self, todo_list):
        task_name = simpledialog.askstring("Input", "Entrez le nom de la tâche:")
        if not task_name:
            messagebox.showerror("Erreur", "Le nom de la tâche est requis!")
            return

        task_image_path = filedialog.askopenfilename(title="Sélectionnez l'image de la tâche",
                                                     filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if not task_image_path:
            messagebox.showerror("Erreur", "Le chemin de l'image est requis!")
            return

        todo_list.add_task(task_name, task_image_path)
        self.save_data()  # Ajoutez cette ligne pour sauvegarder les données

    def remove_list(self, todo_list):
        # Supprime la liste de tâches de la liste interne et de l'interface utilisateur
        self.todo_lists.remove(todo_list)
        self.save_data()
        self.refresh_ui()

    def refresh_ui(self):
        # Rafraîchit l'interface utilisateur en réaffichant toutes les listes
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        for todo_list in self.todo_lists:
            self.display_list(todo_list)

    def display_list(self, todo_list):
        list_frame = tk.Frame(self.list_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, anchor='ne')

        list_label = tk.Label(list_frame, text=f"{todo_list.name} - {todo_list.time}", cursor="hand2")
        list_label.bind("<Button-1>", lambda e: todo_list.show_tasks())
        list_label.pack(side=tk.LEFT)

        add_task_button = tk.Button(list_frame, text="Ajouter une tâche",
                                    command=lambda: self.add_task(todo_list))
        add_task_button.pack(side=tk.LEFT)

        remove_list_button = tk.Button(list_frame, text="Supprimer la liste",
                                       command=lambda: self.remove_list(todo_list))
        remove_list_button.pack(side=tk.RIGHT)
    def save_data(self):
        data = []
        for todo_list in self.todo_lists:
            list_data = {
                'name': todo_list.name,
                'time': todo_list.time,
                'tasks': [{'name': task['name'], 'image_path': task['image_path'], 'checked': task['checked'].get()}
                          for task in todo_list.tasks]
            }
            data.append(list_data)

        with open("data.txt", "w") as f:
            json.dump(data, f)

    def load_data(self):
        try:
            with open("data.txt", "r") as f:
                data = json.load(f)
                for list_data in data:
                    todo_list = TodoList(list_data['name'], list_data['time'])
                    for task_data in list_data['tasks']:
                        task_data['checked'] = tk.BooleanVar(value=task_data['checked'])
                        todo_list.tasks.append(task_data)
                    self.todo_lists.append(todo_list)
                    self.display_list(todo_list)
        except FileNotFoundError:
            pass  # No data file found, start with empty list


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoListManager(root)
    root.mainloop()
