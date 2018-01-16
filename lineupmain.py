from pydfs_lineup_optimizer import Site, Sport, get_optimizer
import os
import kivy
import threading
from functools import partial

from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.logger import Logger


import os

class MyApp(App):
    title = "Fantasy Sports Lineup Optimizer"

class PlayerBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(PlayerBoxLayout,self).__init__(**kwargs)
        self.size_hint_y = None
        self.orientation = 'vertical'
        self.bind(minimum_height=self.setter('height'))
        #for i in range(100):
        #    btn = Button(text=str(i), size_hint_y=None, height=40)
        #    self.add_widget(btn)

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class Root(FloatLayout):
    loadfile = ObjectProperty(None)
    text_input = ObjectProperty(None)

    def __init__(self):
        super(Root,self).__init__()
        self.playersconfig = {}
        self.sitedropdown = DropDown(auto_width=False)
        self.sitedropdown.width = 300
        for site in ['DRAFTKINGS','FANDUEL','YAHOO','FANTASY_DRAFT']:
            btn = Button(text=site,size_hint_y=None, auto_width=False, height=100)
            btn.width = 300
            btn.bind(on_release=lambda btn: self.sitedropdown.select(btn.text))
            self.sitedropdown.add_widget(btn)
        self.sitedropdown.bind(on_select=lambda instance, x: setattr(self.ids.site_button, 'text', x))

        self.sportdropdown = DropDown(auto_width=False)
        self.sportdropdown.width = 300
        for sport in ['BASKETBALL','']:
            btn = Button(text=sport,size_hint_y=None, auto_width=False, height=100)
            btn.width = 300
            #Hack to position button just right, remove if when enable more sports
            if sport != '':
                btn.bind(on_release=lambda btn: self.sportdropdown.select(btn.text))
            self.sportdropdown.add_widget(btn)
        self.sportdropdown.bind(on_select=lambda instance, x: setattr(self.ids.sport_button, 'text', x))

        self.maxlineupdropdown = DropDown(auto_width=False)
        self.maxlineupdropdown.width = 300
        for i in range(1,11):
            btn = Button(text=str(i),size_hint_y=None, auto_width=False, height=100)
            btn.width = 300
            btn.bind(on_release=lambda btn: self.maxlineupdropdown.select(btn.text))
            self.maxlineupdropdown.add_widget(btn)
        self.maxlineupdropdown.bind(on_select=lambda instance, x: setattr(self.ids.max_lineup_button, 'text', x))

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        full_path = os.path.join(path,filename[0])
        self.ids.load_csv_button.text = filename[0]
        players = []
        with open(full_path,'r') as csv_file:
            import csv
            content = csv.reader(csv_file)
            for line in content:
                players.append(line[1])
        self.ids.playerdisplay.clear_widgets()

        headerbox= BoxLayout(orientation='horizontal', size_hint_x=1, size_hint_y=None, height=50)
        headername = Label(text='[b]Name[/b]', markup=True, size_hint=(0.6,1), font_size='11sp', color=(0,0,0,1))
        headerbox.add_widget(headername)
        headerlock = Label(text='[b]Lock[/b]', markup=True, size_hint=(0.1,1), font_size='11sp', color=(0,0,0,1))
        headerbox.add_widget(headerlock)
        headerexposure = Label(text='[b]Exposure[/b]', markup=True, size_hint=(0.4,1), font_size='11sp', color=(0,0,0,1))
        headerbox.add_widget(headerexposure)
        self.ids.playerdisplay.add_widget(headerbox)

        #Remove header in players list
        players.pop(0)
        for player in players:
            prefix = player.replace(' ','')
            playerbox = BoxLayout(orientation='horizontal', size_hint_x=1, size_hint_y=None, height=30)

            playerlabel = Label(text=player, size_hint=(0.6,1), font_size='11sp', color=(0,0,0,1))
            playerlabel.bind(size=playerlabel.setter('text_size'))
            playerbox.add_widget(playerlabel)

            lockcheckbox = CheckBox(size_hint=(0.1,1), id=prefix+'lock')
            playerbox.add_widget(lockcheckbox)

            exposureinput = TextInput(text='0 %',multiline=False, size_hint=(0.4,1), font_size='9sp', id=prefix+'exposure')
            playerbox.add_widget(exposureinput)

            self.ids.playerdisplay.add_widget(playerbox)
        self.dismiss_popup()

    def get_liner(self):
        site=self.ids.site_button.text
        sport=self.ids.sport_button.text
        maxlineup=self.ids.max_lineup_button.text
        ##debug
        #site='DRAFTKINGS'
        #sport='BASKETBALL'
        #maxlineup=10
        ##end debug
        if site == 'Site' or sport == 'Sport' or maxlineup == 'Max Lineup':
            self.dismiss_popup()
            return
        csv_file=self.ids.load_csv_button.text
        ##debug
        #csv_file='DK-NBA.csv'
        ##enddebug
        optimizer = get_optimizer(site,sport)
        optimizer.load_players_from_CSV(csv_file)
        #Exclude header, header is at the end
        for player in self.ids.playerdisplay.children[:-1]:
            if player.children[1].active:
                player_to_lock = optimizer.get_player_by_name(player.children[2].text)
                exposure = float(player.children[0].text.strip(' ').strip('%'))/100
                player_to_lock.max_exposure=exposure
                optimizer.add_player_to_lineup(player_to_lock)

        for playerlog in optimizer.players:
            Logger.info("optimizer:{}".format(playerlog))
        lineup_generator = optimizer.optimize(int(maxlineup))
        #For real
        outputtext='\n'
        for lineup in lineup_generator:
             outputtext += "{}\n\n".format(str(lineup))
        self.get_canvas(outputtext)

    def get_canvas(self, outputtext=None):
        self.ids.rst_doc.text = outputtext
        rst_doc = self.ids.rst_doc
        rst_doc.canvas.before.clear()
        self.ids.secondhalfview.canvas.before.children.insert(0,Color(211/255.0, 211/255.0, 211/255.0, 0.9)) #grey
        self.dismiss_popup()

    def show_output(self):
        content = Label(text='Please Wait...')
        self._popup = Popup(title="App is Processing", content=content, size_hint=(0.9,0.9))
        self._popup.open()
        mythread = threading.Thread(target=partial(self.get_liner))
        mythread.start()

Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)

if __name__ == '__main__':
    MyApp().run()
