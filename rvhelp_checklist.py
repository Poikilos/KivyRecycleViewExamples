from kivy.app import App
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    StringProperty,
    ListProperty,
    BooleanProperty,
    NumericProperty,
)
from kivy.clock import Clock

kv = '''
<ItemRow>:
# This class is used as the viewclass in the RecycleView
# The means this widget will be instanced to view one element of data from the data list.
# The RecycleView data list is a list of dictionaries.  The keys in the dictionary specify the
# attributes of the widget.
    CheckBox:
        id: checkbox
        active: root.mark
        on_release: root.on_checkbox_pressed(root)
    Button:
        text: root.right_text
        on_release: print(f'{self.text} pressed')

BoxLayout:
    orientation: 'vertical'
    Button:
        size_hint_y: None
        height: 48
        text: 'Add widget to RV list'
        on_release: rv.add()

    RV:                          # A Reycleview
        id: rv
        viewclass: 'ItemRow'  # The view class is ItemRow, defined above.
        data: self.rv_data_list  # the data is a list of dicts defined below in the RV class.
        scroll_type: ['bars', 'content']
        bar_width: 10
        RecycleBoxLayout:
            # This layout is used to hold the Recycle widgets
            default_size: None, dp(48)   # This sets the height of the BoxLayout that holds a ItemRow instance.
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height   # To scroll you need to set the layout height.
            orientation: 'vertical'
'''


class ItemRow(BoxLayout):  # The viewclass definitions, and property definitions.
    index = NumericProperty()
    mark = BooleanProperty()
    right_text = StringProperty()

    def on_checkbox_pressed(self, twobuttons):
        self.mark = twobuttons.ids.checkbox.active
        app = App.get_running_app()
        app.root.ids.rv.rv_data_list[self.index]['mark'] = self.mark
        print(f'{self.right_text} checked={self.mark}')


class RV(RecycleView):
    rv_data_list = ListProperty()  # A list property is used to hold the data for the recycleview, see the kv code

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for i in range(2):
            self.rv_data_list.append({
                'index': len(self.rv_data_list),
                'mark': True,
                'right_text': f'Right {i}',
            })
        '''
        This list comprehension is used to create the data list for
        this simple example.
        The data created looks like:
        [{'index': 0, 'mark': True, 'right_text': 'Right 0'},
        {'index': 1, 'mark': True, 'right_text': 'Right 1'},
        {'index': 2, 'mark': True, 'right_text': 'Right 2'},
        {'index': 3, 'mark': True...
        notice the keys in the dictionary correspond to the kivy
        properties in the ItemRow class. The data needs to be in
        this kind of list of dictionary formats.  The RecycleView
        instances the widgets, and populates them with data from this
        list.
        '''
        # Clock.schedule_interval(self.dump_values, 10)

    def dump_values(self, passed_seconds):
        print("* dump_values data={}".format(self.data))

    def add(self):
        index = len(self.rv_data_list)
        self.rv_data_list.append({
            'index': index,
            'mark': False,
            'right_text': f'Added Right {index}',
        })


class RVTwoApp(App):

    def build(self):
        root = Builder.load_string(kv)
        return root


RVTwoApp().run()
