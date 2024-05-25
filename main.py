from kivy.app import App

from sahne import Oyun


from kivy.core.window import Window #deneme
import karakter#deneme
from karakter import Mermi #deneme



class Uygulama(App):
    def build(self):
        
        self.oyun=Oyun()
        return self.oyun

        
if __name__=='__main__':
    Uygulama().run()