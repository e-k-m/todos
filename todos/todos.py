import json
import os
import sys
import tkinter as tk


from todos import scrollframe


class Todo(object):
    def __init__(self, id_, text, complete):
        self.id = id_
        self.text = text
        self.complete = complete

    def __repr__(self):
        return (
            f"Todo(id={self.id}, text={self.text}, complete={self.complete})"
        )

    def __eq__(self, other):
        return (
            self.id == other.id
            and self.text == other.text
            and self.complete == other.complete
        )

    def to_dict(self):
        return {"id": self.id, "text": self.text, "complete": self.complete}

    @staticmethod
    def create_from_dict(d):
        return Todo(d["id"], d["text"], d["complete"])


class Store(object):
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return f"Store(path={self.path})"

    def read(self):
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path) as f:
                return [Todo.create_from_dict(data) for data in json.load(f)]
        except json.decoder.JSONDecodeError:
            return []

    def write(self, todos):
        with open(self.path, "w") as f:
            json.dump([todo.to_dict() for todo in todos], f)


class Model(object):
    def __init__(self, store):
        self.store = store
        self.todos = store.read()
        self.on_todo_list_changed = None

    def bind_todo_list_changed(self, handler):
        self.on_todo_list_changed = handler

    def commit(self, todos):
        if self.on_todo_list_changed is not None:
            self.on_todo_list_changed(todos)
        self.store.write(todos)

    def add_todo(self, todo_text):
        id_ = (
            self.todos[len(self.todos) - 1].id + 1
            if len(self.todos) > 0
            else 1
        )
        self.todos.append(Todo(id_, todo_text, False))
        self.commit(self.todos)

    def edit_todo(self, id_, updated_text):
        self.todos = list(
            map(
                lambda x: (
                    Todo(x.id, updated_text, x.complete) if x.id == id_ else x
                ),
                self.todos,
            )
        )
        self.commit(self.todos)

    def delete_todo(self, id_):
        self.todos = list(filter(lambda x: x.id != id_, self.todos))
        self.commit(self.todos)

    def toggle_todo(self, id_):
        self.todos = list(
            map(
                lambda x: (
                    Todo(x.id, x.text, not x.complete) if x.id == id_ else x
                ),
                self.todos,
            )
        )
        self.commit(self.todos)


class View(object):
    def __init__(self):
        # TODO: Make responsive.
        self.window = tk.Tk()
        self.window.title("todos")
        self.window.geometry("400x500")
        self.window.resizable(False, False)

        header_frame = tk.Frame(master=self.window)
        header_frame.pack(fill=tk.X, side=tk.TOP, expand=True)

        header_label = tk.Label(
            master=header_frame, text="Todos", font=("Arial", 16), width=25
        )
        header_label.pack()

        input_frame = tk.Frame(master=self.window)
        input_frame.pack(padx=5, fill=tk.X, side=tk.TOP, expand=True)

        self.input_entry = input_entry = tk.Entry(master=input_frame)
        input_entry.pack(padx=5, fill=tk.X, side=tk.LEFT, expand=True)

        self.input_button = input_button = tk.Button(
            master=input_frame, text="Add", width=5
        )
        input_button.pack(
            fill=tk.X, side=tk.LEFT,
        )

        scroll_frame = scrollframe.ScrollFrame(self.window, width=300)
        scroll_frame.pack(fill=tk.X, side=tk.TOP, expand=True)

        self.items_frame = items_frame = tk.Frame(master=scroll_frame)
        items_frame.pack(padx=5, fill=tk.X, side=tk.TOP, expand=True)

        self.todos = []

        self.handler_delete = None
        self.handler_edit = None
        self.handler_toggle = None

    def display_todos(self, todos):
        self.delete_todos()
        if not todos:
            item_frame = tk.Frame(master=self.items_frame)
            item_frame.pack()

            item_label = tk.Label(
                master=item_frame,
                text="Nothing to do! Add a todo?",
                font=("Arial", 12),
                width=40,
            )
            item_label.pack()
            self.todos.append((item_frame, item_label))
        else:
            for todo in todos:
                item_frame = tk.Frame(master=self.items_frame)
                item_frame._id = todo.id
                item_frame.pack(
                    padx=5, pady=10, fill=tk.X, side=tk.TOP, expand=True
                )

                item_check_button = tk.Checkbutton(
                    item_frame, variable=tk.IntVar(value=1)
                )
                item_check_button._id = todo.id
                if todo.complete is True:
                    item_check_button.select()
                else:
                    item_check_button.deselect()

                item_check_button.pack(fill=tk.X, side=tk.LEFT)

                item_entry = tk.Entry(master=item_frame, width=45)
                item_entry._id = todo.id
                item_entry.insert(0, todo.text)
                item_entry.pack(padx=5, fill=tk.X, side=tk.LEFT, expand=True)

                item_button = tk.Button(
                    master=item_frame, text="Delete", width=5
                )
                item_button.pack(fill=tk.X, side=tk.LEFT)
                item_button._id = todo.id

                self.todos.append(
                    (item_frame, item_check_button, item_entry, item_button)
                )
                # TODO / FIXME: Reviewe if tkinter has event bubbling.
                # So this would not be needed?
                if self.handler_delete is not None:
                    self.bind_delete_todo(self.handler_delete)

                if self.handler_edit is not None:
                    self.bind_edit_todo(self.handler_edit)

                if self.handler_toggle is not None:
                    self.bind_toggle_todo(self.handler_toggle)

    def delete_todos(self):
        for widgets in self.todos:
            for widget in widgets[::-1]:
                widget.destroy()
        self.todos = []

    def bind_add_todo(self, handler):
        def handle(event):
            todo_text = self.input_entry.get()
            if todo_text:
                handler(todo_text)
            self.input_entry.delete(0, tk.END)

        self.input_button.bind("<Button-1>", handle)
        self.input_entry.bind("<Return>", handle)

    def bind_delete_todo(self, handler):
        if self.handler_delete is None:
            self.handler_delete = handler

        # HACK: len(self.todos) == 2
        if self.todos and len(self.todos[0]) == 2 or not self.todos:
            return

        def handle(event):
            handler(event.widget._id)

        for _, _, _, item_button in self.todos:
            item_button.bind("<Button-1>", handle)

    def bind_edit_todo(self, handler):
        if self.handler_edit is None:
            self.handler_edit = handler

        if self.todos and len(self.todos[0]) == 2 or not self.todos:
            return

        def handle(event):
            handler(event.widget._id, event.widget.get())

        for _, _, item_entry, _ in self.todos:
            item_entry.bind("<FocusOut>", handle)
            item_entry.bind("<Return>", handle)

    def bind_toggle_todo(self, handler):
        if self.handler_toggle is None:
            self.handler_toggle = handler

        if self.todos and len(self.todos[0]) == 2 or not self.todos:
            return

        def handle(event):
            handler(event.widget._id)

        for _, item_check_button, _, _ in self.todos:
            item_check_button.bind("<Button-1>", handle)

    def start(self):
        self.window.mainloop()


class Controller(object):
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.handle_todo_list_changed(self.model.todos)
        self.model.bind_todo_list_changed(self.handle_todo_list_changed)
        self.view.bind_add_todo(self.handle_add_todo)
        self.view.bind_edit_todo(self.handle_edit_todo)
        self.view.bind_delete_todo(self.handle_delete_todo)
        self.view.bind_toggle_todo(self.handle_toggle_todo)

    def handle_todo_list_changed(self, todos):
        self.view.display_todos(todos)

    def handle_add_todo(self, todo_text):
        self.model.add_todo(todo_text)

    def handle_edit_todo(self, id_, todo_text):
        self.model.edit_todo(id_, todo_text)

    def handle_delete_todo(self, id_):
        self.model.delete_todo(id_)

    def handle_toggle_todo(self, id_):
        self.model.toggle_todo(id_)


def main():
    store = Store(os.path.join(os.path.expanduser("~"), ".todos.store"))
    view = View()
    _ = Controller(Model(store), view)
    view.start()
    return 0


if __name__ == "__main__":
    sys.exit(main())
