from kivy.uix.widget import Widget
from kivy.clock import Clock
import random
import karakter
from karakter import Yukle,Zombi, Nine,Mermi,CanGosterge
from kivy.core.window import Window

from kivy.uix.modalview import ModalView #Açılır Pencere
from kivy.clock import mainthread
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.text import LabelBase #harici font eklemek için
from kivy.uix.label import Label 



import gc#deneme





class Oyun(Widget):
    #static değişkenler
    seviyeler={
            1:{'mermiAdet':47,'zombi1':2,'zombi2':2,'zombi3':2,'zombi4':2,'zombi5':2,'zombi6':2},
            2:{'mermiAdet':50,'zombi1':3,'zombi2':2,'zombi3':2,'zombi4':3,'zombi5':2,'zombi6':2},
            3:{'mermiAdet':56,'zombi1':3,'zombi2':3,'zombi3':2,'zombi4':3,'zombi5':3,'zombi6':2},
            4:{'mermiAdet':64,'zombi1':3,'zombi2':3,'zombi3':3,'zombi4':3,'zombi5':3,'zombi6':3},
            5:{'mermiAdet':68,'zombi1':4,'zombi2':3,'zombi3':3,'zombi4':4,'zombi5':3,'zombi6':3},
            6:{'mermiAdet':75,'zombi1':4,'zombi2':4,'zombi3':3,'zombi4':4,'zombi5':4,'zombi6':3},
            7:{'mermiAdet':83,'zombi1':4,'zombi2':4,'zombi3':4,'zombi4':4,'zombi5':4,'zombi6':4},
            8:{'mermiAdet':87,'zombi1':5,'zombi2':4,'zombi3':4,'zombi4':5,'zombi5':4,'zombi6':4},
            9:{'mermiAdet':93,'zombi1':5,'zombi2':5,'zombi3':4,'zombi4':5,'zombi5':5,'zombi6':4},
            10:{'mermiAdet':100,'zombi1':5,'zombi2':5,'zombi3':5,'zombi4':5,'zombi5':5,'zombi6':5}
            }
    sahneZombiSayisiAzami=4 #sahnede aynı anda bulunabilecek maksimum zombi sayısı

    EskiGenislik=Window.width
    EskiYukseklik=Window.height

    arkaPlanDosya='assets/sahne/arkaplan.png'
    acilirPencereYaziTipiIsim='MonsterScratche'
    acilirPencereYaziTipiDosya='assets/fonts/Monster Scratche.ttf'
    silahGostergeYaziTipiIsim='Bullet'
    silahGostergeYaziTipiDosya='assets/fonts/Bulletproof.ttf'

    oyunSonuSayacAzami=30 #Oyun sonu penceresi ne kadar ekranda kalacak

    dosyaAdet=9 #atlas dosyaları yüklenecek sınıfların adedi. Nine,Mermi,Zombi(zombi1),Zombi(zombi2),Zombi(zombi3),Zombi(zombi4),Zombi(zombi5),Zombi(zombi6),CanGosterge
    dosyaYuklemeDurumu={'nine':lambda:Nine.atlasYuklendi,
                        'mermi':lambda:Mermi.atlasYuklendi,
                        'zombi1':lambda:Zombi.atlasYuklendi['zombi1'],
                        'zombi2':lambda:Zombi.atlasYuklendi['zombi2'],
                        'zombi3':lambda:Zombi.atlasYuklendi['zombi3'],
                        'zombi4':lambda:Zombi.atlasYuklendi['zombi4'],
                        'zombi5':lambda:Zombi.atlasYuklendi['zombi5'],
                        'zombi6':lambda:Zombi.atlasYuklendi['zombi6'],
                        'canGosterge':lambda:CanGosterge.atlasYuklendi} # atlas dosyaları yüklenecek olan sınıfların, atlas yükleme durumlarını döndüren lambda fonksiyonları içeren liste


    

    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        
        self.oyunDevam=False #oyunun sonlanıp bitmediğini tutan değişken
        self.seviyeNumara=1 #oyunun kaçıncı seviyesinde
        self.seviye=None # seviyedeki bütün verileri içeren dictionary nesnesi

        self.acilirPencere=None
        self.acilirPencereSaat=None
        self.oyunSonuPencereSayac=-1 #oyun sonu geldiğinde(oyun kaybetti ya da oyun kazandı), açılacak pencerenin ekranda kalış süresi

        #pencereBoyutDegisti fonksiyonunda boyutlandırılacakları için, eğer sahneye eklenmemişse None değere sahip olsunlar
        self.nine=None
        self.mermilerNine=None #Henüz atılmamış mermiler. Ninenin üzerindeki, atılmayı bekleyen mermiler
        self.mermilerSahne=None #Atış yapılarak, sahneye eklenen mermiler
        self.zombilerKulis=None #Henüz sahneye girmemiş olan zombiler
        self.zombilerSahne=None #Sahneye girmiş olan zombiler
        self.arkaPlan=None # oyun arkaplan resmi
        self.seviyeYuklendi=False # her seviyede, sahnedeki nesneler yeniden yüklenecek

        self.bind(size=self.pencereBoyutDegisti)

        #harici font dosyaları ekleniyor
        LabelBase.register(name=Oyun.acilirPencereYaziTipiIsim, fn_regular=Oyun.acilirPencereYaziTipiDosya)
        LabelBase.register(name=Oyun.silahGostergeYaziTipiIsim, fn_regular=Oyun.silahGostergeYaziTipiDosya)
        
        
        self.dosyaYuklePencereAc()




    
    def oyunKaybetti(self):
        self.oyunDevam=False
        self.oyunSaat.cancel()

        for zombi in self.zombilerSahne:
            if zombi.durum!='saldır':
                zombi.animasyonSaat.cancel()

        self.oyunSonuPencereAc('oyun kaybetti pencere')

    def oyunKazandi(self):
        self.oyunDevam=False
        self.oyunSaat.cancel()

        self.seviyeNumara=self.seviyeNumara+1 if self.seviyeNumara<len(Oyun.seviyeler) else 1
        

        self.oyunSonuPencereAc('oyun kazandı pencere')

    def oyunSonuPencereAc(self,oyunSonuTipi):
        self.acilirPencere=AcilirPencere(oyunSonuTipi)
        self.acilirPencereSaat=Clock.schedule_interval(self.oyunSonuTikTak,.1)
    def oyunSonuTikTak(self,dt):
        if self.acilirPencere.durum=='yüklendi':
            if self.acilirPencere.tip=='oyun kazandı pencere' or (self.acilirPencere.tip=='oyun kaybetti pencere' and not self.nine.animasyonSaat):
                self.oyunSonuSayac=0
                self.acilirPencere.open()
                self.ekranTemizle()
        elif self.acilirPencere.durum=='açık':
            self.oyunSonuSayac+=1
            if self.oyunSonuSayac>=Oyun.oyunSonuSayacAzami:
                self.acilirPencere.dismiss()
        elif self.acilirPencere.durum=='kapalı':
            self.acilirPencereSaat.cancel()
                
            self.seviyeYuklePencereAc()


    def dosyaYuklePencereAc(self):
        self.dosyaYuklePencereAcildi=False#dosya yükleme açılır penceresi tamamen açıldığında, dosya yükleme işlemi başlatılacak. Aksi halde açılır pencere görünümünde donmalar oluyor 
        self.acilirPencere=AcilirPencere('dosya yükle pencere')
        self.acilirPencereSaat=Clock.schedule_interval(self.dosyaYuklePencereTikTak,.1)
    def dosyaYuklePencereTikTak(self,dt):
        if self.acilirPencere.durum=='yüklendi':
            self.acilirPencere.open()
        elif self.acilirPencere.durum=='açık':#açılır pencere tamamen açılmadan, dosya yüklemeye başlama. Çünkü açılır pencere görünümünde donmalar oluyor
            if not self.dosyaYuklePencereAcildi:
                self.dosyaYuklePencereAcildi=True
                self.dosyaYukle()
            else:
                dosyaYuklemeSurec=0
                for i in Oyun.dosyaYuklemeDurumu:
                    dosyaYuklemeSurec+=Oyun.dosyaYuklemeDurumu[i]()# atlasları yüklenmiş olan nesneler 1, yüklenmemiş olanlar 0 değerini ekler

                if dosyaYuklemeSurec==Oyun.dosyaAdet:
                    self.acilirPencere.dismiss()
                    self.acilirPencereSaat.cancel()
                    self.seviyeYuklePencereAc()
    @mainthread #ayrı bir thread içerisinde nesne oluşturabilmek için fonksiyonun mainthread olması gerekiyor
    def dosyaYukle(self):
        #Oyunun başında. Tüm atlas dosyaları, 1 kere belleğe yüklenecek

        Yukle.AtlasDosya(Nine)#Oyunun başında. Nine nesnesine ait resimler 1 kere belleğe yüklenecek
        Yukle.AtlasDosya(Mermi)#Oyunun başında. Mermi nesnelerine ait resimler 1 kere belleğe yüklenecek
                        
        #Oyunun başında. Zombi nesnelerine ait resimler 1 kere belleğe yüklenecek
        Yukle.AtlasDosya(Zombi,'zombi1')
        Yukle.AtlasDosya(Zombi,'zombi2')
        Yukle.AtlasDosya(Zombi,'zombi3')
        Yukle.AtlasDosya(Zombi,'zombi4')
        Yukle.AtlasDosya(Zombi,'zombi5')
        Yukle.AtlasDosya(Zombi,'zombi6')
            
        #Oyunun başında. CanGosterge nesnelerine ait resimler 1 kere belleğe yüklenecek
        Yukle.AtlasDosya(CanGosterge)

    def seviyeYuklePencereAc(self):
        self.seviyeYuklePencereAcildi=False#seviye yükleme açılır penceresi tamamen açıldığında, seviye yükleme işlemi başlatılacak. Aksi halde açılır pencere görünümünde donmalar olabilir 
        self.acilirPencere=AcilirPencere('seviye yükle pencere')
        self.acilirPencereSaat=Clock.schedule_interval(self.seviyeYuklePencereTikTak,.1)
    def seviyeYuklePencereTikTak(self,dt):
        
        if self.acilirPencere.durum=='yüklendi':
            self.acilirPencere.open()
        elif self.acilirPencere.durum=='açık':#açılır pencere açılmış durumda ise seviye yükleme başlamış demektir.
            if not self.seviyeYuklePencereAcildi:
                self.seviyeYuklePencereAcildi=True
                self.seviyeYukle()
            else:
                if self.seviyeYuklendi:
                    self.acilirPencere.dismiss()
        elif self.acilirPencere.durum=='kapalı':
            self.acilirPencereSaat.cancel()
            self.oyunBaslatPencereAc()    
    @mainthread #ayrı bir thread içerisinde nesne oluşturabilmek için fonksiyonun mainthread olması gerekiyor
    def seviyeYukle(self):
        self.seviye=Oyun.seviyeler[self.seviyeNumara].copy()#Oyun.seviyeler'den ilgili seviye bilgileri alınıyor
        self.seviyeYuklendi=False

        self.arkaPlan=Image(source=Oyun.arkaPlanDosya,allow_stretch=True,keep_ratio=False,size=(Window.width,Window.height)) # oyun arkaplan resmi
        self.add_widget(self.arkaPlan)

        mermiAdet=self.seviye['mermiAdet']
       

        self.nine=Nine(mermiAdet=mermiAdet)
        self.nine.KonumAyarla()
        self.add_widget(self.nine,0) #z-indeks=0, çünkü nine hep en önde olmalıdır.
        self.add_widget(self.nine.silahGosterge)

        self.mermilerNine=[Mermi(self.nine) for i in range(mermiAdet)]#ninenin sahip olduğu mermiler
        self.mermilerSahne=[]#nine ateş ettiği anda, mermi self.mermilerNine listesinden silinip, bu listeye eklenecek
      

        self.zombilerSahne=[]
        self.zombilerKulis=[]


        zombiSayisi=0
        for zombiTip in reversed(Zombi.Tip):
            zombiSayisi+=self.seviye[zombiTip]

        #Oyuna girecek zombiler sırayla sağ-sol taraf olacak şekilde zombilerKulis listesine ekleniyor
        tarafSayac=0
        zombiSayac=0
        
        while zombiSayac<zombiSayisi:
            zombiTipler=Zombi.Tip.copy()
            while(len(zombiTipler)>0):#aynı tipte zombilerin ardarda gelme olasılığını düşürmek için bu döngü
                rastgeleZombiTip=random.choice(zombiTipler)
                zombiTipler.remove(rastgeleZombiTip)

                if self.seviye[rastgeleZombiTip]>0:
                    self.zombilerKulis.append(Zombi(rastgeleZombiTip,Zombi.Taraf[tarafSayac]))
                    tarafSayac=(tarafSayac+1)%2
                    self.seviye[rastgeleZombiTip]-=1
                    zombiSayac+=1
                    continue      
        self.zombilerKulis.reverse()
        

        for zombi in self.zombilerSahne:
            self.add_widget(zombi,-1)#z-indeks -1, çünkü ninenin arkasında olmalıdır.
            self.add_widget(zombi.canGosterge)
        
        self.seviyeYuklendi=True

    def oyunBaslatPencereAc(self):
        self.acilirPencere=AcilirPencere('oyun başlat pencere',self.seviyeNumara)
        self.acilirPencereSaat=Clock.schedule_interval(self.oyunBaslatPencereTikTak,.1)
    def oyunBaslatPencereTikTak(self,dt):
        
        if self.acilirPencere.durum=='yüklendi':
            self.acilirPencere.open()
        elif self.acilirPencere.durum=='kapalı':
            self.acilirPencereSaat.cancel()
            self.oyunBaslat()
    def oyunBaslat(self):
        self.oyunSaat=Clock.schedule_interval(self.oyunTikTak,1.0/60.0)

        self.oyunDevam=True

        self.zamanSayac=0
        self.zombiSayac=1
                

    def pencereBoyutDegisti(self,*args):
        #burada, sahnedeki bütün nesnelerin boyutları ve hızları güncellenecek 
        if self.arkaPlan:
            self.arkaPlan.size=(Window.width,Window.height)

        if self.nine:
            self.nine.BoyutAyarla()
            self.nine.KonumAyarla()
            self.nine.ZiplaHizHesapla()

        if self.mermilerSahne:
            for mermi in self.mermilerSahne:
                mermi.BoyutAyarla()
                mermi.KonumAyarlaGidis()

        if self.zombilerSahne:
            for zombi in self.zombilerSahne:
                zombi.BoyutAyarla()
                zombi.KonumAyarla()
                zombi.HizHesapla()
                #zombi.TarafGuncelle()

        if self.acilirPencere:
            self.acilirPencere.BoyutAyarla()

        Oyun.EskiGenislik=Window.width
        Oyun.EskiYukseklik=Window.height
    
    def oyunTikTak(self,dt):
        self.zamanSayac+=1

        if not self.oyunDevam:
            return
        
        if len(self.zombilerSahne)==0 and len(self.zombilerKulis)==0:
            self.oyunKazandi()
            return
                
        self.ilerletMermi()
        self.ilerletZombi()

        if self.nine.durum=='tokmakla':
            self.zombiTokmakla()
        
        self.zombiVur()
        self.zombiTemas()
        self.copTemizle()#ölen zombileri, ölen zombilerin can göstergelerini, zombiyi vuran ya da ekrandan çıkan mermileri ekrandan sil


        self.sahneyeZombiEkle()
            
        if self.zamanSayac%300==0:
            gc.collect()
        
    def sahneyeZombiEkle(self):
        zombiSayisi=len(self.zombilerSahne)

        #Eğer sahnede yeterince zombi varsa, bu fonksiyondan çık
        if zombiSayisi>=Oyun.sahneZombiSayisiAzami:
            return
        
        #Eğer sahneye eklenecek zombi kalmamışsa, bu fonksiyondan çık
        if len(self.zombilerKulis)==0:
            return
        
        #Eğer sahneye tam olarak çıkmamış zombi varsa, bu fonksiyondan çık
        for zombi in self.zombilerSahne: 
            if zombi.x<=0 or zombi.right>=Window.width:
                return

        yeniZombi=self.zombilerKulis.pop()
        yeniZombi.SahneyeAyarla()


        self.zombilerSahne.append(yeniZombi)
        self.add_widget(yeniZombi,-1)#z-indeks -1, çünkü ninenin arkasında olmalıdır.
        self.add_widget(yeniZombi.canGosterge)

    def zombiTemas(self):
        if self.nine.durum.split('-')[0]=='zıpla':#eğer durum; zıpla-tüfekli ya da zıpla-tüfeksiz ise
            return
        
        nineSagSinir=self.nine.center_x+Window.width*Nine.genislikOran*Nine.zombiTemasToleransOran
        nineSolSinir=self.nine.center_x-Window.width*Nine.genislikOran*Nine.zombiTemasToleransOran
        for zombi in self.zombilerSahne:
            if zombi.yon=='sola':#zombi sağdan, sola gelirken
                zombiOn=zombi.x
                zombiArka=zombi.right
            else:#zombi soldan, sağa gelirken
                zombiOn=zombi.right
                zombiArka=zombi.x

            if zombiOn<nineSagSinir and zombiOn>nineSolSinir:
                if self.nine.yon!=zombi.yon:#ninenin yüzü zombiye dönükse
                    if self.nine.durum=='tokmakla':#nine zombiyi tokmaklarken temas olursa, nine zarar görmemeli
                        continue
                else:#ninenin arkası zombiye dönükse
                    self.nine.AksiYoneDon()
                if zombi.durum!='saldır':
                    zombi.DurumDegistir('saldır')
                    self.nine.DurumDegistir('öl-tüfekli' if self.nine.tufekVar else 'öl-tüfeksiz')
                    self.oyunKaybetti()
            elif zombiArka<nineSagSinir and zombiArka>nineSolSinir:
                if zombi.durum=='yürü':
                    if zombi.yon=='sola':
                        zombi.right=nineSolSinir
                    else:
                        zombi.x=nineSagSinir
                    zombi.Ezildi()
                         
    def zombiTokmakla(self):
        if self.nine.tokmakVurdu:
            return
        sayac=0
        for zombi in self.zombilerSahne:
            sayac+=1
            if self.nine.yon=='sağa':
                if zombi.taraf=='sağ' and zombi.durum=='yürü':
                    if zombi.center_x<self.nine.tokmakAlaniBaslaSag and zombi.center_x>self.nine.center_x:
                        zombi.center_x=self.nine.tokmakAlaniBaslaSag
                        zombi.Ezildi()
                    

            elif self.nine.yon=='sola':
                if zombi.taraf=='sol' and zombi.durum=='yürü':
                    if zombi.center_x>self.nine.tokmakAlaniBaslaSol and zombi.center_x<self.nine.center_x:
                        zombi.center_x=self.nine.tokmakAlaniBaslaSol
                        zombi.Ezildi()
        self.nine.tokmakVurdu=True
                        
    def zombiVur(self):
        for mermi in self.mermilerSahne:
            if mermi.durum=='gidiş':
                for zombi in self.zombilerSahne:

                    if mermi.durum!='gidiş':#mermi sadece 'gidiş' durumunda ise zombiyi vurabilir
                        continue

                    if zombi.durum=='öl' or zombi=='saldır':#zombi ölürken ya da saldırırken vurulamaz. Yürürken ve yaralı iken vurulabilir
                        continue

                    if zombi.right>Window.width+zombi.width/2 or zombi.x<-zombi.width/2:#zombinin bedeninin en yarısı ekrana girmediyse vurulamaz
                        continue

                    if mermi.yon=='sağa':
                        if mermi.right>=zombi.x and mermi.right<=zombi.right:
                            if mermi.yon==zombi.yon:
                                zombi.AksiYoneGit()

                            zombi.Vuruldu()
                            mermi.VurmaKonumXYHesapla(zombi)
                            mermi.DurumDegistir('vurma')
                            
                    elif mermi.yon=='sola':
                        if mermi.x<=zombi.right and mermi.x>=zombi.x:
                            if mermi.yon==zombi.yon:
                                zombi.AksiYoneGit()
                                
                            zombi.Vuruldu()
                            mermi.VurmaKonumXYHesapla(zombi)
                            mermi.DurumDegistir('vurma')
    
    def sehneyeMermiEkle(self):#Nine, ateş ettiği anda mermilerNine'den bir mermi eksilt ve mermilerSahne'ye ekle
        mermi=self.mermilerNine.pop()
        mermi.SahneyeAyarla(self.nine)
        self.mermilerSahne.append(mermi)
        self.add_widget(mermi)

    def ilerletMermi(self):
        for mermi in self.mermilerSahne:
            if mermi.durum=='gidiş':
                mermi.x+=mermi.hiz

                #ekrandan çıkan mermiler
                if mermi.yon=='sağa' and mermi.right>Window.width:
                    mermi.sil=True
                elif mermi.yon=='sola' and mermi.x<0:
                    mermi.sil=True

    def ilerletZombi(self):
        for sira,zombi in enumerate(self.zombilerSahne):
            if zombi.durum=='yürü':                          
                zombi.x+=zombi.hiz
                zombi.TarafGuncelle()
                if zombi.yon=='sağa' and zombi.right>self.width:
                    zombi.AksiYoneGit()
                elif zombi.yon=='sola' and zombi.x<0:
                    zombi.AksiYoneGit()
            
            self.zombiKarsilasma(zombi,sira+1)

    def ninedenKac(self):#Nine zıpladığında, nineye doğru yürüyen tüm zombiler geri dönsün
        for zombi in self.zombilerSahne:
            if zombi.durum=='öl':
                continue
            if (zombi.taraf=='sağ' and zombi.yon=='sola') or (zombi.taraf=='sol' and zombi.yon=='sağa'):
                zombi.AksiYoneGit()
    
    def mermiSil(self,mermi):#Mermi nesnesini ekrandan kaldırır ve oyundan siler. Bu fonksiyondan önce mermilerSahne ve mermilerNine listelerinden kaldırılmalıdır. 
        self.remove_widget(mermi)#mermi, oyun sahnesinden kaldırılıyor
        del mermi#mermi nesnesini oyundan sil
    def zombiSil(self,zombi):#Zombi ve ona ait CanGosterge nesnelerini ekrandan kaldırır ve oyundan siler. Bu fonksiyondan önce zombiler listesinden kaldırılmalıdır. 
        self.remove_widget(zombi.canGosterge)#zombi ile birlikte, zombiye ait CanGosterge nesnesinin sahneden kaldırılması gerekiyor
        self.remove_widget(zombi)#zombi nesnesi sahneden kaldırılıyor

        del zombi.canGosterge#canGosterge nesnesini oyundan sil
        del zombi#zombi nesnesini oyundan sil
    def nineSil(self):#Nine ve ona ait SilahGosterge nesnelerini ekrandan kaldırır ve oyundan siler.
        self.remove_widget(self.nine.silahGosterge)#nineye ait olan, SilahGosterge nesnesi oyun sahnesinden kaldırılıyor
        self.remove_widget(self.nine) #nine, oyun sahnesinden kaldırılıyor

        del self.nine.silahGosterge #nineye ait olan, SilahGosterge nesnesi oyundan siliniyor
        del self.nine #nine nesnesini oyundan sil
    def arkaPlanSil(self):#Arkaplan resmini ekrandan kaldırır ve oyundan siler.
        self.remove_widget(self.arkaPlan) #arkaplan resmi, oyun sahnesinden kaldırılıyor
        del self.arkaPlan #arkaplan resmi, oyundan siliniyor

    def copTemizle(self):#ölen zombileri ve zombiyi vuran ya da ekrandan çıkan mermileri temizle
        for mermi in self.mermilerSahne:
            if mermi.sil:
                self.mermilerSahne.remove(mermi)#mermi, listeden kaldırılıyor
                self.mermiSil(mermi)
        
        for zombi in self.zombilerSahne:
            if zombi.sil:
                self.zombilerSahne.remove(zombi)#zombi, listeden kaldırılıyor
                self.zombiSil(zombi)
        
        
        #gc.collect()#oyundan silinen nesnelerin, bellekten de silinmesi için
    def ekranTemizle(self):#nine öldüğünde ya da bir sonraki seviyeye geçilirken, ekrandaki tüm nesneleri temizle
        self.nineSil()

        while len(self.mermilerSahne)>0:
            mermi=self.mermilerSahne.pop()#mermi, listeden kaldırılıyor
            self.mermiSil(mermi)

        while len(self.mermilerNine):
            mermi=self.mermilerNine.pop()#mermi, listeden kaldırılıyor
            self.mermiSil(mermi)

        while len(self.zombilerSahne)>0:
            zombi=self.zombilerSahne.pop()#zombi, listeden kaldırılıyor
            self.zombiSil(zombi)
        
        self.arkaPlanSil()

        gc.collect()#oyundan silinen nesnelerin, bellekten de silinmesi için

    def zombiKarsilasma(self,zombi,sira):
        #zombi ile sahnedeki diğer zombilerin karşılaşıp karşılaşmadığını test et
        if zombi.durum=='öl':
            return
        for digerZombi in self.zombilerSahne[sira:]:
            if digerZombi.durum=='öl':
                continue

            if zombi.taraf==digerZombi.taraf:
                if zombi.yon=='sağa':
                    if zombi.right>digerZombi.x and zombi.right<digerZombi.right:
                        zombi.AksiYoneGit()
                        if digerZombi.yon=='sola':
                            digerZombi.AksiYoneGit()
                    elif digerZombi.right>zombi.x and digerZombi.right<zombi.right:
                        digerZombi.AksiYoneGit()
                elif zombi.yon=='sola':
                    if zombi.x<digerZombi.right and zombi.x>digerZombi.x:
                        zombi.AksiYoneGit()
                        if digerZombi.yon=='sağa':
                            digerZombi.AksiYoneGit()
                    elif digerZombi.x<zombi.right and digerZombi.x>zombi.x:
                        digerZombi.AksiYoneGit()
            elif zombi.taraf=='sağ' and digerZombi.taraf=='sol':
                if zombi.yon=='sağa':
                    if zombi.x<=digerZombi.right and zombi.right>=digerZombi.right:
                        if digerZombi.yon=='sağa':
                            digerZombi.AksiYoneGit()
                elif zombi.yon=='sola':
                    if zombi.x<=digerZombi.right and zombi.x>=digerZombi.x:
                        zombi.AksiYoneGit()
                        if digerZombi.yon=='sağa':
                            digerZombi.AksiYoneGit()
            elif zombi.taraf=='sol' and digerZombi.taraf=='sağ':
                if zombi.yon=='sağa':
                    if zombi.right>=digerZombi.x and zombi.right<=digerZombi.right:
                        zombi.AksiYoneGit()
                        if digerZombi.yon=='sola':
                            digerZombi.AksiYoneGit()
                elif zombi.yon=='sola':
                    if zombi.right>=digerZombi.x and zombi.right<=digerZombi.right:
                        if digerZombi.yon=='sola':
                            if digerZombi.durum=='yürü':
                                digerZombi.AksiYoneGit()
    

    def on_touch_down(self,touch):
        if self.oyunDevam:
            if touch.y<Window.height/2:#ekranın alt kısmına dokunulmuşsa
                if self.nine.durum.split('-')[0]=='zıpla':# nine zıplama durumundayken ekranın altına dokunulursa nine, ateş etmeden ve tokmaklamadan zemine insin. 
                    self.nine.DurumDegistir('bekle-tüfekli' if self.nine.tufekVar else 'bekle-tüfeksiz')
                else: # nine zıplama durumunda değilken, ekranın altına dokunulursa
                    if touch.x<Window.width/2: # ekranın sol tarafına dokunulursa
                        self.nine.YonAyarla('sola')

                        if self.nine.tufekVar:
                            self.nine.DurumDegistir('ateş et')
                            self.sehneyeMermiEkle()
                        else:
                            self.nine.DurumDegistir('tokmakla')

                    else: # ekranın sağ tarafına dokunulursa
                        self.nine.YonAyarla('sağa')

                        if self.nine.tufekVar:
                            self.nine.DurumDegistir('ateş et')
                            self.sehneyeMermiEkle()
                        else:
                            self.nine.DurumDegistir('tokmakla')
            else:#ekranın üst kısmına dokunulmuşsa, nine zıplasın
                if self.nine.durum.split('-')[0]=='bekle':
                    self.nine.DurumDegistir('zıpla-tüfekli' if self.nine.tufekVar else 'zıpla-tüfeksiz')
                    self.ninedenKac()

            
class DugmeOyna(Image):
    orijinalGenislik=1200
    orijinalYukseklik=414
    resimNormalPng='assets/sahne/oynaNormal.png'
    resimBasiliPng='assets/sahne/oynaBasili.png'
    
    def __init__(self,ebeveynPencere,**kwargs):
        super().__init__(**kwargs)

        self.keep_ratio=False
        self.allow_stretch=True
        self.ebeveynPencere=ebeveynPencere
        self.resimNormal=Image(source=DugmeOyna.resimNormalPng)
        self.resimBasili=Image(source=DugmeOyna.resimBasiliPng)
        self.texture=self.resimNormal.texture
        

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.texture=self.resimBasili.texture
        return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.texture=self.resimNormal.texture
            self.ebeveynPencere.dismiss()
        return super().on_touch_up(touch)

class AcilirPencere(ModalView):
    logo='assets/sahne/logo.png'
    logoOrijinalGenislik=2000
    logoOrijinalYukseklik=2116

    #Her açılır pencere tipi için yalnızca tek bir Label nesnesi kullanılacak
    etiketRenk=[.894,.157,.157,1]       #etiketin yazı rengi
    etiketBoyutOran={'dosya yükle pencere':.05,'seviye yükle pencere':.05,'oyun başlat pencere':.15,'oyun kaybetti pencere':.15,'oyun kazandı pencere':.15}#Etiketin, yazı boyutunun pencere yüksekliğine oranı
    etiketYazi={'dosya yükle pencere':u'DOSYALAR Y\u00dbKLEN\u00ceYOR','seviye yükle pencere':u'OYUN Y\u00dbKLEN\u00ceYOR','oyun başlat pencere':u'SEV\u00ceYE ','oyun kaybetti pencere':u'OYUN B\u00ceTT\u00ce','oyun kazandı pencere':u'TEBR\u00ceKLER'}

    pencereGenislikOran=.9     #Açılır pencerenin genişliğinin, ana pencerenin genişliğine oranı
    pencereYukseklikOran=.9    #Açılır pencerenin yüksekliğinin, ana pencerenin yüksekliğine oranı


    
    def __init__(self,tip,seviyeNumara=-1,**kwargs):
        super().__init__(**kwargs)

        self.background=''
        self.background_color=[.129,.094,.247,.7]


        self.durum='yükleniyor' # açık, kapalı, yükleniyor, yüklendi
        self.tip=tip    #dosya yükle pencere,seviye yükleme pencere,oyun başlat pencere, oyun kaybetti pencere, oyun kazandı pencere
        self.auto_dismiss=False
        self.seviyeNumara=seviyeNumara#Eğer tip='oyun başlat pencere' ise kullanılacak değişken

        

        self.etiket=Label()
        self.etiket.font_name=Oyun.acilirPencereYaziTipiIsim
        self.etiket.color=AcilirPencere.etiketRenk
        self.etiket.text=AcilirPencere.etiketYazi[self.tip]

        
        
        
        
        self.pencereBoyutAyarla()

        
        if self.tip=='dosya yükle pencere' or self.tip=='seviye yükle pencere':
            self.yukleniyorPencereAyarla()
        elif self.tip=='oyun başlat pencere':
            self.oyunBaslatPencereAyarla()
        elif self.tip=='oyun kaybetti pencere' or self.tip=='oyun kazandı pencere':#oyun sonu: oyun kaybetti ya da oyun kazandı anlamına gelebilir
            self.oyunSonuPencereAyarla()


        self.durum='yüklendi'
        

    def BoyutAyarla(self):
        self.pencereBoyutAyarla()

        self.etiketBoyutAyarla(self.tip)
        if self.tip=='dosya yükle pencere' or self.tip=='seviye yükle pencere':
            self.logoBoyutAyarla()
        elif self.tip=='oyun başlat pencere':
            self.dugmeOynaBoyutAyarla()
        elif self.tip=='oyun kaybetti pencere' or self.tip=='oyun kazandı pencere':
            pass
    
    def etiketBoyutAyarla(self,tip):
        self.etiket.font_size=self.height*AcilirPencere.etiketBoyutOran[tip]

    def pencereBoyutAyarla(self):
        self.size_hint=None,None
        self.width=Window.width*AcilirPencere.pencereGenislikOran
        self.height=Window.height*AcilirPencere.pencereYukseklikOran

    def yukleniyorPencereAyarla(self):
        yerlesim=BoxLayout(orientation='vertical')

        self.logo=Image(source=AcilirPencere.logo,allow_stretch=False,keep_ratio=True)
        self.logo.size_hint=None,None
        self.logoBoyutAyarla()

        self.etiketBoyutAyarla(self.tip)

        yerlesim.add_widget(self.logo)
        yerlesim.add_widget(self.etiket)
        self.add_widget(yerlesim)
    
    def logoBoyutAyarla(self):
        self.logo.width=self.width
        self.logo.height=self.height*.8

    def oyunBaslatPencereAyarla(self):
        yerlesim=FloatLayout()

        self.etiket.text+=str(self.seviyeNumara)
        self.etiket.size_hint=None,None
        self.etiketBoyutAyarla(self.tip)
        self.etiket.pos_hint={'center_x':.5,'top':.8}

        self.dugmeOyna=DugmeOyna(self)
        self.dugmeOyna.size_hint=None,None
        self.dugmeOynaBoyutAyarla()
        self.dugmeOyna.pos_hint={'center_x':.5,'y':.2}

        yerlesim.add_widget(self.etiket)
        yerlesim.add_widget(self.dugmeOyna)
        self.add_widget(yerlesim)       

    def dugmeOynaBoyutAyarla(self):
        self.dugmeOyna.height=self.height/5
        self.dugmeOyna.width=self.dugmeOyna.height*DugmeOyna.orijinalGenislik/DugmeOyna.orijinalYukseklik

    def oyunSonuPencereAyarla(self):
        self.etiketBoyutAyarla(self.tip)
        self.etiket.size_hint=None,None
        self.etiket.pos_hint={'center_x':.5,'top':.8}


        self.add_widget(self.etiket)

    def on_pre_open(self):
        self.durum='açık'
        return super().on_pre_open()

    def on_dismiss(self):
        self.durum='kapalı'
        return super().on_dismiss()
    





        


        
        
        