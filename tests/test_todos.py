import os
import unittest

from todos import todos


class TestTodo(unittest.TestCase):
    def test_create(self):
        _ = todos.Todo(1, "Buy milk", False)

    def test_to_dict(self):
        todo = todos.Todo(1, "Buy milk", False)
        self.assertTrue(todo, {"id": 1, "text": "Buy milk", "complete": False})

    def test_create_from_dict(self):
        todo = todos.Todo.create_from_dict(
            {"id": 1, "text": "Buy milk", "complete": False}
        )
        self.assertEqual(todo.id, 1)
        self.assertEqual(todo.text, "Buy milk")
        self.assertEqual(todo.complete, False)

    def test_repr(self):
        todo = todos.Todo(1, "Buy milk", False)
        self.assertTrue(todo.__repr__())


class TestStore(unittest.TestCase):
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "tmp.store"
    )

    def setUp(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def tearDown(self):
        self.setUp()

    def test_create(self):
        _ = todos.Store(self.path)

    def test_write(self):
        store = todos.Store(self.path)
        store.write([todos.Todo(1, "Buy milk", False)])

    def test_read(self):
        store = todos.Store(self.path)
        self.assertEqual(store.read(), [])

        r = [todos.Todo(1, "Buy milk", False)]
        store.write(r)
        self.assertEqual(store.read(), r)

    def test_repr(self):
        store = todos.Store(self.path)
        self.assertTrue(store.__repr__())


class TestModel(unittest.TestCase):

    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "tmp.store"
    )

    def setUp(self):
        if os.path.exists(self.path):
            os.remove(self.path)

        self.store = todos.Store(self.path)

    def tearDown(self):
        self.setUp()

    def test_create(self):
        _ = todos.Model(self.store)

    def test_add_todo(self):
        model = todos.Model(self.store)
        model.add_todo("Buy milk")
        self.assertEqual(model.todos, [todos.Todo(1, "Buy milk", False)])

    def test_bind_todo_list_chanced(self):
        model = todos.Model(self.store)

        def handle_todo_list_changed(r):
            self.assertTrue(r, [todos.Todo(1, "Buy milk", False)])

        model.bind_todo_list_changed(handle_todo_list_changed)
        model.add_todo("Buy milk")

    def test_edit_todo(self):
        model = todos.Model(self.store)
        model.edit_todo(1, "Buy cheese")
        self.assertEqual(model.todos, [])

        model.add_todo("Buy milk")
        self.assertEqual(model.todos, [todos.Todo(1, "Buy milk", False)])
        model.edit_todo(1, "Buy cheese")
        self.assertEqual(model.todos, [todos.Todo(1, "Buy cheese", False)])

    def test_delete_todo(self):
        model = todos.Model(self.store)
        model.delete_todo(1)
        self.assertEqual(model.todos, [])

        model.add_todo("Buy milk")
        self.assertEqual(model.todos, [todos.Todo(1, "Buy milk", False)])
        model.delete_todo(1)
        self.assertEqual(model.todos, [])

    def test_toggle_todo(self):
        model = todos.Model(self.store)
        model.toggle_todo(1)
        self.assertEqual(model.todos, [])

        model.add_todo("Buy milk")
        self.assertEqual(model.todos, [todos.Todo(1, "Buy milk", False)])
        model.toggle_todo(1)
        self.assertEqual(model.todos, [todos.Todo(1, "Buy milk", True)])


class TestView(unittest.TestCase):
    # TODO: Full UI testing, not just 'smoke tests'.
    def test_create(self):
        _ = todos.View()

    def test_display_todos(self):
        view = todos.View()
        view.display_todos([])


class TestController(unittest.TestCase):
    # TODO: Full UI testing.
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "tmp.store"
    )

    def setUp(self):
        if os.path.exists(self.path):
            os.remove(self.path)

        self.model = todos.Model(todos.Store(self.path))
        self.view = todos.View()

    def tearDown(self):
        self.setUp()

    def test_create(self):
        _ = todos.Controller(self.model, self.view)

    def test_handle_todo_list_changed(self):
        controller = todos.Controller(self.model, self.view)
        controller.handle_todo_list_changed([])

    def test_handle_add_todo(self):
        controller = todos.Controller(self.model, self.view)
        controller.handle_add_todo("Buy milk")
        self.assertEqual(
            controller.model.todos, [todos.Todo(1, "Buy milk", False)]
        )

    def test_handle_edit_todo(self):
        controller = todos.Controller(self.model, self.view)
        controller.handle_add_todo("Buy milk")
        controller.handle_edit_todo(1, "Buy cheese")
        self.assertEqual(
            controller.model.todos, [todos.Todo(1, "Buy cheese", False)]
        )

    def test_handle_delete_todo(self):
        controller = todos.Controller(self.model, self.view)
        controller.handle_add_todo("Buy milk")
        controller.handle_delete_todo(1)
        self.assertEqual(controller.model.todos, [])

    def test_handle_toggle_todo(self):
        controller = todos.Controller(self.model, self.view)
        controller.handle_add_todo("Buy milk")
        controller.handle_toggle_todo(1)
        self.assertEqual(
            controller.model.todos, [todos.Todo(1, "Buy milk", True)]
        )


if __name__ == "__main__":
    unittest.main()
