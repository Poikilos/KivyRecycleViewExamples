# KivyRecycleViewExamples
The purpose of this repo is to track the correct way to use the Kivy RecycleView which replaces the ListView. This repo is based on rv_help by ElliotG including a Python version added for https://groups.google.com/g/kivy-users/c/P0c44_otKcI?pli=1

If you need to fix certain issues in your non-KV Python Kivy code quickly, you may want to look at the following commits:
- (2fc75c4)[https://github.com/poikilos/KivyRecycleViewExamples/commit/2fc75c46ad803a2863d908c5e16a6c6487b49b02] Synchronize rv.data with rv_data using Python (handle a change event for a property, and in this case, set a RecycleView's data to a ListProperty).
- (2fc75c4)[https://github.com/poikilos/KivyRecycleViewExamples/commit/2fc75c46ad803a2863d908c5e16a6c6487b49b02] Set viewclass using Python.
- (8e7127b)[https://github.com/poikilos/KivyRecycleViewExamples/commit/8e7127b6ddff2509212bdf06229d29bc38de1f68] Synchronize the key and label text using Python.
- (8e7127b)[https://github.com/poikilos/KivyRecycleViewExamples/commit/8e7127b6ddff2509212bdf06229d29bc38de1f68] Set text color on a label.
- (ec47d8c)[https://github.com/poikilos/KivyRecycleViewExamples/commit/ec47d8caabee9b8b3a240c98a56afec1a9bfa501] Feed data back into the ListProperty that acts as the data source. The following code changes in the commit are unrelated:
  - `root = Builder.load_string(kv); return root` is no different than `return Builder.load_string(kv)`. `app.root` is generated automatically regardless, and root in the case of this code is an ambiguous local variable that is unnecessary.
  - `Clock.schedule_interval(self.dump_values, 1)` and the `dump_values` method are only for debugging purposes, to prove that the ListProperty was changed by `on_checked_changed`


## What doesn't work
This code was removed. The commits above are correct, whereas the code (included below for reference) was removed because it doesn't work:
```Python
class ItemRow(RecycleDataViewBehavior, BoxLayout):
    def __init__(self, **kwargs):
        # RecycleDataViewBehavior.__init__(**kwargs)
        # BoxLayout.__init__(**kwargs)
        # ^ doesn't help, because __init__ is never called

        # ...

    # ...


class ItemScreen(Screen):
    def __init__(self, **kwargs):
        # NOTE: build is only for App.
        super().__init__(**kwargs)
        echo1("* ItemScreen init")
        # self.bind(on_size=self.custom_on_size)
        # ^ fails silently
        # self.on_size = self.custom_on_size
        # ^ fails silently
        self.bgColor = Color(1, 1, 1, 1, mode='rgba')
        self.bgRect = Rectangle()
        self.canvas.before.add(self.bgColor)
        self.canvas.before.add(self.bgRect)
        # ^ NOTE: Change rect size to screen,
        #   but on_size only occurs for ScreenManager not Screen.

    # ...

class ItemScreens(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("* ItemScreens init")
        screen = ItemScreen()
        self.screen = screen
        # self.add_widget(screen)
        # self.bind(on_size=self.on_size_change)

    # ...
```
- `self.bind(on_size=self.on_size_change)`: "AttributeError: 'ItemScreens' object has no attribute 'on_size'. Did you mean: 'on_size_change'?"

```Python
class HybridRowsApp(App):

    # ...

    def build(self):

        # ...

        # self.bind(on_size=screen.custom_on_size)
        # ^ fails silently
        # self.on_size=self.custom_on_size
        # ^ fails silently

        echo1("  * building Screen manually in App")

        # bgColor = Color(1, 1, 1, 1, mode='rgba')
        # screen.canvas.add(bgColor)
        # bgRect.bind(size=screen.size.setter('size'))
        # bgRect = Rectangle(pos=screen.pos, size_hint=(1.0, 1.0))
        # ^ doesn't help
        # screen.canvas.before.add(bgColor)
        # bgRect = Rectangle(pos=screen.pos, size=screen.size)
        # screen.size = ListProperty(screen.size)
        # bgRect.size is a tuple

        # bgRect = Rectangle()
        # screen.bgRect = bgRect
        # echo1("type(bgRect.size):{}"
        #       "".format(type(bgRect.size).__name__))

        # screen.bind(width=screen.setter('width'))
        # ^ fails silently

        # screen.canvas.before.add(bgRect)

        # rv = KeyedView(viewclass=ItemRow)
        # ^ accepts viewclass or view_adapter
        # ^ doesn't work: the form is blank; type(rv.viewclass) NoneType
        rv = KeyedView()
        # type(rv.viewclass) is NoneType regardless of what is passed
        #   to the constructor.
        echo0("type(rv.viewclass): {}"
              "".format(type(rv.viewclass).__name__))

        # ...

        # self.bind(on_size=screen.custom_on_size)
        # ^ fails silently
        # self.on_size=self.custom_on_size
        # ^ fails silently

        echo1("  * building Screen manually in App")

        # bgColor = Color(1, 1, 1, 1, mode='rgba')
        # screen.canvas.add(bgColor)
        # bgRect.bind(size=screen.size.setter('size'))
        # bgRect = Rectangle(pos=screen.pos, size_hint=(1.0, 1.0))
        # ^ doesn't help
        # screen.canvas.before.add(bgColor)
        # bgRect.size is a tuple, so try making it into a list property:

        # bgRect = Rectangle(pos=screen.pos, size=screen.size)
        # screen.size = ListProperty(screen.size)

        # bgRect = Rectangle()
        # screen.bgRect = bgRect
        # echo1("type(bgRect.size):{}"
        #       "".format(type(bgRect.size).__name__))

        # screen.bind(width=screen.setter('width'))
        # ^ fails silently

        # screen.canvas.before.add(bgRect)
        # ^ commented since nothing seems to work to make the rect match
        #   the size of the container :(

        # rv = KeyedView(viewclass=ItemRow)
        # ^ accepts viewclass or view_adapter
        # ^ doesn't work: the form is blank; type(rv.viewclass) NoneType
        rv = KeyedView()
        # type(rv.viewclass) is NoneType regardless of what is passed
        #   to the constructor.
        echo0("type(rv.viewclass): {}"
              "".format(type(rv.viewclass).__name__))

        self.rv = rv
        # rv.viewclass = "ItemRow"
        # ^ doesn't work (the form is blank)
        # rv.viewclass = ItemRow
        # ^ doesn't work (the form is blank)

        # See <kivy.org/doc/stable/api-kivy.uix.recycleview.views.html>:
        '''
        "The view module handles converting the data to a view using
        the adapter class which is then displayed by the layout. A
        view can be any Widget based class. However, inheriting from
        RecycleDataViewBehavior adds methods for converting the data
        to a view."
        '''
        #
        # rv.recycleview = ItemRow
        # ^ doesn't work (the form is blank)
        # itemrow = ItemRow()
        # self.rv.attach_recycleview(itemrow)
```
- `screen.size = ListProperty(screen.size)`: "ValueError: ItemScreen.size must be a list or a tuple type"
- `bgRect.bind(size=screen.size.setter('size'))`: "AttributeError: 'kivy.graphics.vertex_instructions.Rectangle' object has no attribute 'bind'"
- `self.rv.attach_recycleview(itemrow)`: "AttributeError: 'KeyedView' object has no attribute 'attach_recycleview'"
  - <https://kivy.org/doc/stable/api-kivy.uix.recycleview.views.html> says "Associates a RecycleViewBehavior with this instance. It is stored in recycleview."

TLDR: The above code doesn't work. Use the included python files instead to fix the error messages that are noted in this readme for the purpose of you finding this document. See the top of this document for more information on the exact fixes.
