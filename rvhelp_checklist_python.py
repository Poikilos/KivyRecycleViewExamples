from kivy.app import App
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.properties import (
    StringProperty,
    ListProperty,
    BooleanProperty,
    NumericProperty,
)
from kivy.clock import Clock


class TwoButtons(BoxLayout):  # The viewclass definitions, and property definitions.
    index = NumericProperty()
    active = BooleanProperty()
    right_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        active_cb = CheckBox(active=self.active, on_release=lambda x: self.on_checked_changed(x))
        self.active_cb = active_cb
        self.add_widget(active_cb)
        right_button = Button(text=self.right_text, on_release=lambda x: print(f'{self.right_text} pressed'))
        self.add_widget(right_button)
        self.right_button = right_button

    def on_checked_changed(self, twobuttons):
        if self.active != twobuttons.active:
            self.active = twobuttons.active
            app = App.get_running_app()
            app.root.rv.rv_data_list[self.index]['active'] = self.active
        # else don't trigger an infinite loop.

    def on_active(self, twobuttons, v):
        '''
        If checked using the checkbox, the following is always true
        because on_checked_changed sets active:
        `twobuttons.active_cb.active == v`
        but that's ok because the checkbox should only be set if the
        active BooleanProperty changes externally.
        '''
        print("on_active(twobuttons, {}) self.right_button.text:{}"
              "".format(v, self.right_button.text))
        if twobuttons.active_cb.active != v:
            twobuttons.active_cb.active = v
            twobuttons.right_button.text = str(v)
        # else don't trigger infinite loop

    def on_right_text(self, obj, v):
        print("on_right_text({}, {}) self.right_button.text:{}"
              "".format(obj, v, self.right_button.text))
        self.right_button.text = v


class RBL(RecycleBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.default_size = (None, 48)
        self.default_size_hint = (1, None)
        self.size_hint_y = None
        self.orientation = 'vertical'

    def on_minimum_height(self, obj, v):
        self.height = self.minimum_height


class RV(RecycleView):
    rv_data_list = ListProperty()  # A list property is used to hold the data for the recycleview, see the kv code

    def on_rv_data_list(self, *args):
        self.data = self.rv_data_list

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for i in range(2):
            self.rv_data_list.append({
                'index': len(self.rv_data_list),
                'active': True,
                'right_text': f'Right {i}',
            })
        # This list comprehension is used to create the data list for this simple example.
        # The data created looks like:
        # [{'left_text': 'Left 0', 'right_text': 'Right 0'}, {'left_text': 'Left 1', 'right_text': 'Right 1'},
        # {'left_text': 'Left 2', 'right_text': 'Right 2'}, {'left_text': 'Left 3'},...
        # notice the keys in the dictionary correspond to the kivy properties in the TwoButtons class.
        # The data needs to be in this kind of list of dictionary formats.  The RecycleView instances the
        # widgets, and populates them with data from this list.
        Clock.schedule_once(self.set_viewclass)  # schedule setting the viewclass
        self.scroll_type = ['bars', 'content']
        self.bar_width = 10
        self.add_widget(RBL())

        Clock.schedule_interval(self.dump_values, 1)

    def dump_values(self, passed_seconds):
        print("* dump_values data={}".format(self.data))

    def set_viewclass(self, _):
        self.viewclass = TwoButtons

    def add(self, *args):
        index = len(self.rv_data_list)
        self.rv_data_list.append({
            'index': index,
            'active': False,
            'right_text': f'Added Right {index}',
        })


class RootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.rv = RV()    # the RecycleView
        button = Button(size_hint_y=None, height=48, text='Add Widget to RV list',
                        on_release=self.rv.add)
        self.add_widget(button)
        self.add_widget(self.rv)


class RVTwoApp(App):
    def build(self):
        self.root = RootWidget()
        return self.root


RVTwoApp().run()
