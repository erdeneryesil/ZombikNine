from kivy.core.window import Window
from kivy.uix.image import Image,CoreImage
from kivy.clock import Clock
from kivy.atlas import Atlas
from kivy.uix.label import Label 

from kivy.lang import Builder
Builder.load_file('dizayn.kv')



#nine ve zombi karakterlerini sola ya da sağa doğru döndürmek için kullanılacak açı değerleri
YDondurmeAci={'sola':0,'sağa':180}

#nine ve zombi karakterlerini sola ya da sağa doğru döndüren fonksiyon
def AciTersle(karakter):
        karakter.aci=YDondurmeAci[karakter.yon]

#nine ve zombi karakterlerinin ekrandaki y koordinatının, ekran genişliğine oranı
YKonumOran=.22

class Yukle:
    @staticmethod
    def AtlasDosya(Sinif,zombiTip=None):
        if zombiTip:
            atlasDizin=Sinif.dizin+'/'+zombiTip+'/'
            kare=Sinif.kare[zombiTip]
        else:
            atlasDizin=Sinif.dizin+'/'
            kare=Sinif.kare 

        if zombiTip:Sinif.atlasYuklendi[zombiTip]=0
        else:Sinif.atlasYuklendi=0

        for durum in kare:#tüm .atlas dosyalarını dolaşan döngü
            #atlasDosyaTek=Atlas(Sinif.dizin+'/'+Sinif.atlasDosya[durum])#.atlas dosyaları teker teker ele alınıyor
            atlasDosyaTek=Atlas(atlasDizin+Sinif.atlasDosya[durum])#.atlas dosyaları teker teker ele alınıyor
            for key in atlasDosyaTek.textures.keys():#her .atlas dosyası içindeki resimleri dolaşan döngü
                hamKare=CoreImage(atlasDosyaTek[key])#.atlas dosyası içindeki, resimler teker teker ele alınıyor
                kare[durum].append(hamKare)#resim dosyaları CanGosterge.kare nesnesine aktarılıyor
        
        if zombiTip:Sinif.atlasYuklendi[zombiTip]=1
        else:Sinif.atlasYuklendi=1
        
        

class Mermi(Image):
    #static değişkenler
    dizin='assets/mermi' #merminin resim dosyalarının bulunduğu dizin
    atlasDosya={'patlama':'patlama.atlas','gidiş':'gidis.atlas','vurma':'vurma.atlas'}
    orijinalGenislik={'patlama':90,'gidiş':30,'vurma':150}
    orijinalYukseklik={'patlama':90,'gidiş':20,'vurma':150}
    gecikme={'patlama':.01,'gidiş':1,'vurma':.05 } #DİKKAT: merminin vurma(12x.05) ile zombinin yaralan(20x.03) gecikmeleri uyumlu olmalı  
    kareSayisi={'patlama':7,'gidiş':1,'vurma':12} 
    hizOran=.02
    kare={'patlama':[],'gidiş':[],'vurma':[]}# animasyonların içerdiği resimler. ZipDosyaYukle fonksiyonunda yüklenecek
    genislikOranPatlama=.0625#patlama genişliğinin, ekran genişliğine oranı. ninenin boyutuyla orantılı olmalı.
    genislikOranGidis=.0625#gidiş genişliğinin, ekran genişliğine oranı. ninenin boyutuyla orantılı olmalı.
    atlasYuklendi=0 # atlas dosyalarının yüklenip yğklenmediğini kontrol edeceğimiz değişken. Yüklendiğine 1 olacak

    def __init__(self,nine,**kwargs):
        super().__init__(**kwargs)
        #Mermi nesnesi, oluşturulurduğunda sahnede görünmeyecek. Nine ateş ettiğinde sahnede görünecek. 
        #O yüzden durum, boyut ve konumla ilgili ayarların kurucuda yapılmasına gerek yok.
        #Mermi nesnesi sahneye ekleneceği zaman yapılmalı

        self.genislikOranVurma=-1 ## 'vurma' genişliği vurulan zombi boyutuyla orantılı olmalı. o yüzden genislikOranPatlama,genislikOranGidiş aksine static değil
        self.durum='' #'patlama','gidiş','vurma'. Şu an boş, SahneyeAyarla fonksiyonunda ayarlanacak
        
        self.konumY={'patlama':-1,'gidiş':-1,'vurma':-1} #BaslangicKonumHesapla fonksiyonunda, değerleri hesaplanacak
        self.konumX={'patlama':-1,'gidiş':-1,'vurma':-1} #BaslangicKonumHesapla fonksiyonunda, değerleri hesaplanacak
        

        #bu 3 değer, mermi sahneye girdiği anda YonAyarla fonksiyonu tarafından berirlenecek
        self.yon=''
        self.aci=-1
        self.hiz=-1

        self.allow_stretch=True

        self.kareSayac=0
        self.animasyonSaat=None

        #self.DurumDegistir(self.durum)

        self.sil=False #görevi bittiğinde True olacak

    def SahneyeAyarla(self,nine):
        #Mermi nesnesi, oluşturulurduğunda sahnede görünmeyecek. Nine ateş ettiğinde sahnede görünecek. 
        #O yüzden boyut ve konumla ilgili ayarların kurucuda yapılmasına gerek yok.
        #Mermi nesnesi sahneye ekleneceği zaman yapılmalı
        self.DurumDegistir('patlama')
        self.baslangicKonumHesapla(nine)
        self.BoyutAyarla()
        self.KonumAyarla()
        self.yonAyarla(nine.yon)
        

    def baslangicKonumHesapla(self,nine):#'patlama' ve 'gidiş' durumlarında mermi, nineye göre konumlandırılacak
        #aşağıdaki değişkenler, kullanılacak sabit değerler
        konumXKatsayiPatlama=0.3 #mermi patlarken, nineye göre yatayda konumlandırılırken kullanılacak katsayı
        konumXKatsayiGidis=0.1 #mermi gitmeye başladığı anda, nineye göre yatayda konumlandırılırken kullanılacak katsayı
        konumYKatsayiPatlama=0.5 #patlama esnasında, nineye göre dikeyde konumlandırılırken kullanılacak katsayı
        konumYKatsayiGidis=0.25 #gidiş esnasında, nineye göre dikeyde konumlandırılırken kullanılacak katsayı

        patlamaResimGenislik=Window.width*Mermi.genislikOranPatlama
        patlamaResimYukseklik=Mermi.orijinalYukseklik['patlama']*(patlamaResimGenislik/Mermi.orijinalGenislik['patlama'])
        gidisResimGenislik=Window.width*Mermi.genislikOranGidis*Mermi.orijinalGenislik['gidiş']/Mermi.orijinalGenislik['patlama']
        gidisResimYukseklik=Mermi.orijinalYukseklik['gidiş']*(gidisResimGenislik/Mermi.orijinalGenislik['gidiş'])

        #self.konumX['vurma'], #self.konumY['vurma'] değerleri, zombi vurulduğunda belli olacak

        self.konumY['patlama']=nine.y+nine.height*konumYKatsayiPatlama-patlamaResimYukseklik
        self.konumY['gidiş']=nine.y+nine.height*konumYKatsayiGidis-gidisResimYukseklik

        if nine.yon=='sağa':
            self.konumX['patlama']=nine.right-nine.width*konumXKatsayiPatlama
            self.konumX['gidiş']=nine.right-nine.width*konumXKatsayiGidis
        elif nine.yon=='sola':
            patlamaResimGenislik=Window.width*Mermi.genislikOranPatlama
            self.konumX['patlama']=(nine.x+nine.width*konumXKatsayiPatlama)-patlamaResimGenislik
            gidisResimGenislik=Window.width*Mermi.genislikOranPatlama*Mermi.orijinalGenislik['gidiş']/Mermi.orijinalGenislik['patlama']
            self.konumX['gidiş']=(nine.x+nine.width*konumXKatsayiGidis)-gidisResimGenislik

    def yonAyarla(self,yon):
        self.yon=yon
        self.aci=YDondurmeAci[self.yon]
        self.hiz=Window.width*Mermi.hizOran if self.yon=='sağa' else -Window.width*Mermi.hizOran
    def BoyutAyarla(self):
        #resmin genişliğini, ekran genişliğine göre belirle. Sonra yüksekliği de aynı oranda hesapla
        #resimin hem genişliğinin hem yükseklğinin ayrı ayrı hesaplanması ve aynı zamanda genişlik/yükseklik oranının korunması gerekiyor      
        if self.durum=='patlama':
            genislikOran=Mermi.genislikOranPatlama
        elif self.durum=='gidiş':
            genislikOran=Mermi.genislikOranGidis
        elif self.durum=='vurma':
            genislikOran= self.genislikOranVurma

        self.width=Window.width*genislikOran*Mermi.orijinalGenislik[self.durum]/Mermi.orijinalGenislik['patlama']

        self.height=Mermi.orijinalYukseklik[self.durum]*(self.width/Mermi.orijinalGenislik[self.durum])
    def KonumAyarlaGidis(self):
        #Eğer mermi giderken, pencerenini boyutu değişirse
        from sahne import Oyun #circular import : sahne modülünde, karakter modülü import edildiği için burada sahne modülünü sayfanın en üstünde import edemiyoruz
        self.x/=Oyun.EskiGenislik/Window.width
        self.y/=Oyun.EskiYukseklik/Window.height

    def KonumAyarla(self):      
        self.y=self.konumY[self.durum]
        self.x=self.konumX[self.durum]        

    def VurmaKonumXYHesapla(self,zombi):
        self.vurmaBoyutOraniHesapla(zombi)
        vurmaResimGenislik=Window.width*self.genislikOranVurma*Mermi.orijinalGenislik['vurma']/Mermi.orijinalGenislik['patlama']
        vurmaResimYukseklik=Mermi.orijinalYukseklik['vurma']*(vurmaResimGenislik/Mermi.orijinalGenislik['vurma'])

        self.konumX['vurma']=zombi.x+(zombi.width-vurmaResimGenislik)/2
        self.konumY['vurma']=zombi.y+(zombi.height-vurmaResimYukseklik)/2


    def vurmaBoyutOraniHesapla(self,zombi):
        self.genislikOranVurma=Zombi.genislikOran[zombi.tip]

        

    def DurumDegistir(self,durum):        
        self.durum=durum
        self.animasyonHazirlik()

    def animasyonHazirlik(self):
        self.texture=Mermi.kare[self.durum][0].texture#yeni durumun, ilk karesi alınıyor. Durum geçişinde, önceki durumun karesi kalmasın diye
        self.BoyutAyarla()
        self.KonumAyarla()

        self.kareSayac=0
        if self.animasyonSaat:
            self.animasyonSaat.cancel()
        self.animasyonSaat=Clock.schedule_interval(self.animasyonTikTak,Mermi.gecikme[self.durum])

    def animasyonTikTak(self,dt):
        if self.durum!='gidiş':
            self.texture=Mermi.kare[self.durum][self.kareSayac].texture
            self.kareSayac+=1
        if Mermi.kareSayisi[self.durum]>1 and self.kareSayac+1==Mermi.kareSayisi[self.durum]: #'gidiş' gibi tek resimli durumlarda animasyonun bitip bitmediğini kontrol etmeye gerek yok 
            if self.durum=='patlama':
                self.DurumDegistir('gidiş')
            elif self.durum=='vurma':
                self.sil=True
                self.animasyonSaat.cancel()

class SilahGosterge(Image):
    resimGenislikOran=.1 #tüfek ve tokmak resim genişliklerinin, ekranın genişliğine oranı
    resimOrijinalGenislik={'tüfek':206,'tokmak':206}
    resimOrijinalYukseklik={'tüfek':67,'tokmak':136}
    resimPng={'tüfek':'assets/sahne/tufek.png','tokmak':'assets/sahne/tokmak.png'}

    yKonumOran=.9#resim ve etiketlerin ekrandaki y koordinatının, ekran genişliğine oranı
    xKonumOranResim=.1#tüfek ya da tokmak resminin ekrandaki x koordinatının, ekran genişliğine oranı
    xKonumOranEtiket=.2#mermi sayısı etiketinin ekrandaki x koordinatının, ekran genişliğine oranı

    etiketRenk=[.651,.231,.176] #etiketin yazı rengi
    etiketBoyutOran=.05        #etiketin, yazı boyutunun pencere yüksekliğine oranı

    def __init__(self,mermiAdet,**kwargs):
        super().__init__(**kwargs)

        self.allow_stretch=True

        self.resim={'tüfek':Image(source=SilahGosterge.resimPng['tüfek']),'tokmak':Image(source=SilahGosterge.resimPng['tokmak'])}
        
        from sahne import Oyun #circular import : sahne modülünde, karakter modülü import edildiği için burada sahne modülünü sayfanın en üstünde import edemiyoruz
        self.etiket=Label(color=SilahGosterge.etiketRenk,font_name=Oyun.silahGostergeYaziTipiIsim)
        self.durum=''#'tüfek','tokmak'
        if mermiAdet>0:
            self.etiket.text=str(mermiAdet)
            self.DurumDegistir('tüfek')
        else:
            self.DurumDegistir('tokmak')


    def DurumDegistir(self,durum):
        self.durum=durum
        self.texture=self.resim[self.durum].texture
        if self.durum=='tüfek':
            if not(self.etiket in self.children):
                self.add_widget(self.etiket)
        elif self.durum=='tokmak':
            if self.etiket in self.children:
                self.remove_widget(self.etiket)
        
        self.BoyutAyarla()
        self.KonumAyarla()
            
    def BoyutAyarla(self):
        #resmin genişliğini, ekran genişliğine göre belirle. Sonra yüksekliği de aynı oranda hesapla
        #resimin hem genişliğinin hem yükseklğinin ayrı ayrı hesaplanması ve aynı zamanda genişlik/yükseklik oranının korunması gerekiyor
  
        self.width=Window.width*SilahGosterge.resimGenislikOran
        self.height=SilahGosterge.resimOrijinalYukseklik[self.durum]*(self.width/SilahGosterge.resimOrijinalGenislik[self.durum])
        if self.durum=='tüfek':
            self.etiket.font_size=Window.width*SilahGosterge.etiketBoyutOran

    def KonumAyarla(self):
        self.center_x=Window.width*SilahGosterge.xKonumOranResim
        self.center_y=Window.height*SilahGosterge.yKonumOran
        if self.durum=='tüfek':
            self.etiket.center_x=Window.width*SilahGosterge.xKonumOranEtiket
            self.etiket.center_y=Window.height*SilahGosterge.yKonumOran
    
    def MermiAdetDegistir(self,mermiAdet):
        self.etiket.text=str(mermiAdet)

class Nine(Image):
    #static değişken
    genislikOran=.1#.2#ninenin genişliğinin, ekranın genişliğine oranı
    #orijinalOlTufekliGenislik=215
    orijinalGenislik={'ateş et':215,'bekle-tüfekli':214,'bekle-tüfeksiz':185,'öl-tüfekli':400,'öl-tüfeksiz':347,'tokmakla':616,'zıpla-tüfekli':500,'zıpla-tüfeksiz':404}
    orijinalYukseklik={'ateş et':239,'bekle-tüfekli':239,'bekle-tüfeksiz':239,'öl-tüfekli':325,'öl-tüfeksiz':325,'tokmakla':383,'zıpla-tüfekli':588,'zıpla-tüfeksiz':476}
    
    tokmakGenislikFarki=54 #'tokmakla' genişliği ile  'bekle-tüfeksiz' genişliği arasındaki farkı kompanze etmek için kullanılan katsayı
    #tokmak alanı: zombilerin tokmaktan etkilenebileceği alan
    tokmakAlaniOran=.22 #tokmak alanının, tokmaklama esnasındaki ninenin genişliğine oranı
    tokmakAlaniOnBoslukOran=0.034 # tokmaklama alanının ucunda küçük bir boş alan var resimde. Bu boşluğun, tokmaklama esnasındaki ninenin genişliğine oranı
    tokmakAlaniUzunluk=-1 #tokmak alanının uzunluğu
    tokmakAlaniBaslaSag=-1#sağ tarafı tokmaklarken, zombileri etkileyebilecek olan tokmak alanının başlangıç noktası
    tokmakAlaniBitisSag=-1#sağ tarafı tokmaklarken, zombileri etkileyebilecek olan tokmak alanının bitiş noktası
    tokmakAlaniBaslaSol=-1#sol tarafı tokmaklarken, zombileri etkileyebilecek olan tokmak alanının başlangıç noktası
    tokmakAlaniBitisSol=-1#sol tarafı tokmaklarken, zombileri etkileyebilecek olan tokmak alanının bitiş noktası

    ziplaYukseklikOran=.9 #zıpladığında y değerinin alabileceği en büyük değerin, ekran yüksekliğine oranı

    zombiTemasToleransOran=.25#.25 # zombi ne kadar yaklaştığında temas etti sayılacak? Bu değer arttıkça, zombi daha uzaktan temas edebilecek.

    dizin='assets/nine' #ninenin resim dosyalarının bulunduğu dizin


    atlasDosya={'öl-tüfekli':'ol-tufekli.atlas', 
        'öl-tüfeksiz':'ol-tufeksiz.atlas', 
        'ateş et':'ates-et.atlas',
        'tokmakla':'tokmakla.atlas',
        'bekle-tüfekli':'bekle-tufekli.atlas',
        'bekle-tüfeksiz':'bekle-tufeksiz.atlas',
        'zıpla-tüfekli':'zipla-tufekli.atlas',
        'zıpla-tüfeksiz':'zipla-tufeksiz.atlas'} # animasyon dosyaları
    
    kareSayisi={'öl-tüfekli':50, 
        'öl-tüfeksiz':50, 
        'ateş et':15,
        'tokmakla':20,
        'bekle-tüfekli':20,
        'bekle-tüfeksiz':20,
        'zıpla-tüfekli':25,#'zıpla-tüfekli' ve 'zıpla-tüfeksiz' aynı kare sayısına sahip olmalı
        'zıpla-tüfeksiz':25#'zıpla-tüfekli' ve 'zıpla-tüfeksiz' aynı kare sayısına sahip olmalı
        } #animasyonların içerdiği resim sayısı.
    kare={'öl-tüfekli':[], 
        'öl-tüfeksiz':[], 
        'ateş et':[],
        'tokmakla':[],
        'bekle-tüfekli':[],
        'bekle-tüfeksiz':[],
        'zıpla-tüfekli':[],
        'zıpla-tüfeksiz':[]
        }# animasyonların içerdiği resimler. AtlasDosyaYukle fonksiyonunda yüklenecek
    gecikme={
        'öl-tüfekli':.05, 
        'öl-tüfeksiz':.05, 
        'ateş et':.01,
        'tokmakla':.02,
        'bekle-tüfekli':.1,
        'bekle-tüfeksiz':.1,
        'zıpla-tüfekli':.04,#'zıpla-tüfekli' ve 'zıpla-tüfeksiz' aynı gecikmeye sahip olmalı
        'zıpla-tüfeksiz':.04#'zıpla-tüfekli' ve 'zıpla-tüfeksiz' aynı gecikmeye sahip olmalı
        } # animasyonların gecikme süreleri
    
    atlasYuklendi=0 # atlas dosyalarının yüklenip yğklenmediğini kontrol edeceğimiz değişken. Yüklendiğine 1 olacak
    
    def __init__(self,mermiAdet,**kwargs):
        super().__init__(**kwargs)
       
        self.mermiAdet=mermiAdet
        if self.mermiAdet>0:
            self.durum='bekle-tüfekli' #'öl-tüfekli', 'öl-tüfeksiz', 'ateş et','tokmakla','bekle-tüfekli','bekle-tüfeksiz','zıpla-tüfekli','zıpla-tüfeksiz'
            self.tufekVar=True # tüfeğin olup olmadığı
        else:
            self.durum='bekle-tüfeksiz' #'öl-tüfekli', 'öl-tüfeksiz', 'ateş et','tokmakla','bekle-tüfekli','bekle-tüfeksiz','zıpla-tüfekli','zıpla-tüfeksiz'
            self.tufekVar=False # tüfeğin olup olmadığı
        
        self.silahGosterge=SilahGosterge(self.mermiAdet)

        self.tokmakVurdu=False # tokmağın tek vuruşta sadece tek bir can eksiltmesi için

        self.kareSayac=0
        self.animasyonSaat=None

        self.yon='sağa'
        self.aci=YDondurmeAci[self.yon]

        self.allow_stretch=True
        self.ziplaHizOrijinal={'zıpla-tüfekli':-1,'zıpla-tüfeksiz':-1} #zıplarken ziplaHiz azalacak ve artacak ama bu değer sabit kalacak
        self.ziplaHiz=-1
        self.ziplaHizDegisim={'zıpla-tüfekli':-1,'zıpla-tüfeksiz':-1} #zıplarken ziplaHiz değerinin ne kadar artıp azalacağı
        self.ZiplaHizHesapla()
        self.DurumDegistir(self.durum)

   
    def DurumDegistir(self,durum):
        self.durum=durum
        self.animasyonHazirlik()  

    def animasyonHazirlik(self):
        self.texture=Nine.kare[self.durum][0].texture#yeni durumun, ilk karesi alınıyor. Durum geçişinde, önceki durumun karesi kalmasın diye 
        self.BoyutAyarla()
        self.KonumAyarla()

        if self.durum=='tokmakla':
            self.tokmakVurdu=False
        elif self.durum=='ateş et':
            self.mermiAdet-=1
            self.silahGosterge.MermiAdetDegistir(self.mermiAdet)
            if self.mermiAdet==0:
                self.tufekVar=False
                self.silahGosterge.DurumDegistir('tokmak')
        elif self.durum.split('-')[0]=='zıpla':#eğer durum, zıpla-tüfekli ya da zıpla-tüfeksiz ise
            self.ziplaHiz=self.ziplaHizOrijinal[self.durum]


        self.kareSayac=0
        if self.animasyonSaat:
            self.animasyonSaat.cancel()
        self.animasyonSaat=Clock.schedule_interval(self.animasyonTikTak,Nine.gecikme[self.durum])

    def animasyonTikTak(self,dt):
        self.texture=Nine.kare[self.durum][self.kareSayac].texture
        self.kareSayac+=1

        if self.durum.split('-')[0]=='zıpla':#eğer durum, zıpla-tüfekli ya da zıpla-tüfeksiz ise
            self.zipla() 
        if self.kareSayac==Nine.kareSayisi[self.durum]:
            #if self.durum.split('-')[0]=='zıpla':#eğer durum, zıpla-tüfekli ya da zıpla-tüfeksiz ise
                #self.ziplaHiz*=-1#zıpla-tüfekli ya da zıpla-tüfeksiz durumları sona erdiyse, ziplaHiz yeniden pozitif değerde olmalı
                #self.DurumDegistir('bekle-tüfekli' if self.tufekVar else 'bekle-tüfeksiz')   
            if self.durum.split('-')[0]=='öl':#eğer durum, öl-tüfekli ya da öl-tüfeksiz ise
                self.animasyonSaat.cancel()
                self.animasyonSaat=None
            else:
                self.DurumDegistir('bekle-tüfekli' if self.tufekVar else 'bekle-tüfeksiz')
                
            

    def BoyutAyarla(self):
        #resmin genişliğini, ekran genişliğine göre belirle. Sonra yüksekliği de aynı oranda hesapla
        #resimin hem genişliğinin hem yükseklğinin ayrı ayrı hesaplanması ve aynı zamanda genişlik/yükseklik oranının korunması gerekiyor
  
        self.width=Window.width*Nine.genislikOran*Nine.orijinalGenislik[self.durum]/Nine.orijinalGenislik['bekle-tüfeksiz']
        self.height=Nine.orijinalYukseklik[self.durum]*(self.width/Nine.orijinalGenislik[self.durum])#*Nine.orijinalYukseklik[self.durum]/Nine.orijinalYukseklik['bekle-tüfekli' if self.tufekVar else 'bekle-tüfeksiz']
        
        self.silahGosterge.BoyutAyarla()

    def KonumAyarla(self):
        if self.durum=='tokmakla':
            if self.yon=='sağa':
                self.center_x=Window.width/2+(self.width/Nine.orijinalGenislik['tokmakla'])*Nine.tokmakGenislikFarki
            elif self.yon=='sola':
                self.center_x=Window.width/2-(self.width/Nine.orijinalGenislik['tokmakla'])*Nine.tokmakGenislikFarki
            
            self.tokmakAlaniHesapla()
        else:
            self.center_x=Window.width/2
            
        self.y=Window.height*YKonumOran

        self.silahGosterge.KonumAyarla()

    def yonTersle(self):
        if self.yon=='sola':
            self.yon='sağa'
        elif self.yon=='sağa':
            self.yon='sola'

    def AksiYoneDon(self):
        self.yonTersle()
        AciTersle(self)
    
    def YonAyarla(self,yon):
        self.yon=yon
        self.aci=YDondurmeAci[yon]

    def tokmakAlaniHesapla(self):#KonumAyarla içerisinden çağırılacak
        Nine.tokmakAlaniUzunluk=self.width*Nine.tokmakAlaniOran
        tokmakAlaniOnBoslukUzunluk=self.width*Nine.tokmakAlaniOnBoslukOran

        Nine.tokmakAlaniBaslaSag=self.right-tokmakAlaniOnBoslukUzunluk
        Nine.tokmakAlaniBitisSag=self.tokmakAlaniBaslaSag-self.tokmakAlaniUzunluk
        Nine.tokmakAlaniBaslaSol=self.x+tokmakAlaniOnBoslukUzunluk
        Nine.tokmakAlaniBitisSol=self.tokmakAlaniBaslaSol+self.tokmakAlaniUzunluk
    
    def ZiplaHizHesapla(self):
        #ninenin zıplama hızı, ekranın yüksekliğine göre ayarlanacak
        ziplamaKareSayisi=Nine.kareSayisi['zıpla-tüfekli']

        nineTufekliGenislik=Window.width*Nine.genislikOran*Nine.orijinalGenislik['zıpla-tüfekli']/Nine.orijinalGenislik['bekle-tüfeksiz']
        nineTufekliYukseklik=Nine.orijinalYukseklik['zıpla-tüfekli']*(nineTufekliGenislik/Nine.orijinalGenislik['zıpla-tüfekli'])
        nineTufeksizGenislik=Window.width*Nine.genislikOran*Nine.orijinalGenislik['zıpla-tüfeksiz']/Nine.orijinalGenislik['bekle-tüfeksiz']
        nineTufeksizYukseklik=Nine.orijinalYukseklik['zıpla-tüfeksiz']*(nineTufeksizGenislik/Nine.orijinalGenislik['zıpla-tüfekli'])


        ziplamaTufekliMesafe=Window.height*Nine.ziplaYukseklikOran-(self.y+nineTufekliYukseklik) #zıplarken katedilecek mesafe
        self.ziplaHizOrijinal['zıpla-tüfekli']=(2*ziplamaTufekliMesafe)/ziplamaKareSayisi
        self.ziplaHizDegisim['zıpla-tüfekli']=self.ziplaHizOrijinal['zıpla-tüfekli']/(ziplamaKareSayisi/2)

        ziplamaTufeksizMesafe=Window.height*Nine.ziplaYukseklikOran-(self.y+nineTufeksizYukseklik) #zıplarken katedilecek mesafe
        self.ziplaHizOrijinal['zıpla-tüfeksiz']=(2*ziplamaTufeksizMesafe)/ziplamaKareSayisi
        self.ziplaHizDegisim['zıpla-tüfeksiz']=self.ziplaHizOrijinal['zıpla-tüfeksiz']/(ziplamaKareSayisi/2)

    def zipla(self):
        #ninenin zıplarken konum değiştirmesini sağlar
        self.y+=self.ziplaHiz
        self.ziplaHiz-=self.ziplaHizDegisim[self.durum]
        
class CanGosterge(Image):
    #static değişkenler
    orijinalGenislik=45
    orijinalYukseklik=90
    genislikOran=.04
    dizin='assets/can_gosterge'
    gecikme=.1 # animasyonların gecikme süreleri. Hepsinde aynı
    kareSayisi=12   #hepsi aynı sayıda resim içeriyor
    tipSayisi=7 #7 çeşit CanGosterge tipi var
    atlasDosya={0:'0.atlas',1:'1.atlas',2:'2.atlas',3:'3.atlas',4:'4.atlas',5:'5.atlas',6:'6.atlas'} # animasyon dosyaları
    kare={0:[],1:[],2:[],3:[],4:[],5:[],6:[]}# animasyonların içerdiği resimler. zipDosyaYukle fonksiyonunda yüklenecek
    atlasYuklendi=0 # atlas dosyalarının yüklenip yğklenmediğini kontrol edeceğimiz değişken. Yüklendiğine 1 olacak
    
    def __init__(self,zombi,**kwargs):
        super().__init__(**kwargs)

        self.zombi=zombi # hangi zombinin can sayısı gösterecek
        self.deger=zombi.canSayisi #0,1,2,3,4,5,6 

        self.kareSayac=0                                                                        
        self.animasyonSaat=None

        self.allow_stretch=True
        self.opacity=0 # başlangıçta görünmez olacak. zombi vurulduğunda, kısa süreli olarak görünecek            

    def BoyutAyarla(self):
        #resmin genişliğini, ekran genişliğine göre belirle. Sonra yüksekliği de aynı oranda hesapla
        #resimin hem genişliğinin hem yükseklğinin ayrı ayrı hesaplanması ve aynı zamanda genişlik/yükseklik oranının korunması gerekiyor
        
        self.width=Window.width*CanGosterge.genislikOran
        self.height=CanGosterge.orijinalYukseklik*(self.width/CanGosterge.orijinalGenislik)

    def konumAyarla(self):
        #bazı zombiler ölürken genişliği arttığı için, anlık genişlik değil, genel genişliğine göre konumlandırılacak 
        zombiGenislik=Window.width*Zombi.genislikOran[self.zombi.tip]
        if self.zombi.taraf=='sağ':
            self.center_x=self.zombi.x+zombiGenislik/2
        elif self.zombi.taraf=='sol':
            self.center_x=self.zombi.right-zombiGenislik/2
        
        self.y=self.zombi.top

    def DegerDegistir(self,deger):            
        self.deger=deger
        self.animasyonaHazirlik()
    
    def animasyonaHazirlik(self):
        self.texture=CanGosterge.kare[self.deger][0].texture#yeni durumun, ilk karesi alınıyor. Durum geçişinde, önceki durumun karesi kalmasın diye 
        self.BoyutAyarla()
        self.konumAyarla()
        
        self.kareSayac=0
        if self.animasyonSaat:
            self.animasyonSaat.cancel()
        self.animasyonSaat=Clock.schedule_interval(self.animasyonTikTak,CanGosterge.gecikme)

    def animasyonTikTak(self,dt):
        self.texture=CanGosterge.kare[self.deger][self.kareSayac].texture
        self.kareSayac+=1
        if self.kareSayac==CanGosterge.kareSayisi:
            self.opacity=0 #animasyon bittiğinde yeniden görünmez olacak
            self.animasyonSaat.cancel()#animasyonun devam etmemesi için, self.animasyonSaat iptal ediliyor 

class Zombi(Image):
    #static değişkenler

    #resimlerin orijinal genişlik ve yükseklikleri
    orijinalYuruGenislik={'zombi1':177,'zombi2':181,'zombi3':175,'zombi4':375,'zombi5':374,'zombi6':374}
    orijinalYuruYukseklik={'zombi1':242,'zombi2':247,'zombi3':223,'zombi4':366,'zombi5':367,'zombi6':396}
    orijinalSaldirGenislik={'zombi1':212,'zombi2':207,'zombi3':192,'zombi4':440,'zombi5':442,'zombi6':442}
    orijinalSaldirYukseklik={'zombi1':239,'zombi2':249,'zombi3':234,'zombi4':350,'zombi5':345,'zombi6':374} 
    orijinalOlGenislik={'zombi1':327,'zombi2':327,'zombi3':324,'zombi4':441,'zombi5':434,'zombi6':444}
    orijinalOlYukseklik={'zombi1':244,'zombi2':242,'zombi3':233,'zombi4':362,'zombi5':356,'zombi6':394}
    orijinalYaralanGenislik={'zombi1':212,'zombi2':207,'zombi3':192,'zombi4':440,'zombi5':442,'zombi6':442}
    orijinalYaralanYukseklik={'zombi1':239,'zombi2':249,'zombi3':234,'zombi4':350,'zombi5':345,'zombi6':374} 
    orijinalEzilGenislik={'zombi1':212,'zombi2':207,'zombi3':192,'zombi4':440,'zombi5':442,'zombi6':442}
    orijinalEzilYukseklik={'zombi1':239,'zombi2':249,'zombi3':234,'zombi4':350,'zombi5':345,'zombi6':374} 
    orijinalGenislik={'yürü':orijinalYuruGenislik,'saldır':orijinalSaldirGenislik,'öl':orijinalOlGenislik,'yaralan':orijinalYaralanGenislik,'ezil':orijinalEzilGenislik}
    orijinalYukseklik={'yürü':orijinalYuruYukseklik,'saldır':orijinalSaldirYukseklik,'öl':orijinalOlYukseklik,'yaralan':orijinalYaralanYukseklik,'ezil':orijinalEzilYukseklik}

    Taraf=['sol','sağ']
    Tip=['zombi1','zombi2','zombi3','zombi4','zombi5','zombi6']
    genislikOran={'zombi1':.08,'zombi2':.08,'zombi3':.08,'zombi4':.13,'zombi5':.13,'zombi6':.13}#zombi tiplerinin genişliğinin, ekranın genişliğine oranı
    hizOran={'zombi1':.0015,'zombi2':.00175,'zombi3':.002,'zombi4':.00225,'zombi5':.0025,'zombi6':.00275}#zombi türlerinin hareket etme hızının, ekranın genişliğine oranı
    canlar={'zombi1':1,'zombi2':2,'zombi3':3,'zombi4':4,'zombi5':5,'zombi6':6}#zombi türlerinin türlerine göre, sahip olacakları can sayıları
    dizin='assets/zombiler'#zombilerin resim dosyalarının bulunduğu dizin

    atlasDosya={'öl':'ol.atlas','saldır':'saldir.atlas','yürü':'yuru.atlas','yaralan':'yaralan.atlas','ezil':'ezil.atlas'} # animasyon dosyaları
    gecikme={'öl':.1,'saldır':.12,'yürü':.1,'yaralan':.03,'ezil':.02} # animasyonların gecikme süreleri.#DİKKAT: merminin vurma(12x.05) ile zombinin yaralan(20x.03) gecikmeleri uyumlu olmalı 

    kareSayisi={'zombi1':{'öl':20,'saldır':20,'yürü':16,'yaralan':20,'ezil':20},
                'zombi2':{'öl':20,'saldır':20,'yürü':16,'yaralan':20,'ezil':20},
                'zombi3':{'öl':20,'saldır':20,'yürü':16,'yaralan':20,'ezil':20},
                'zombi4':{'öl':16,'saldır':16,'yürü':16,'yaralan':16,'ezil':16},
                'zombi5':{'öl':16,'saldır':16,'yürü':16,'yaralan':16,'ezil':16},
                'zombi6':{'öl':16,'saldır':16,'yürü':16,'yaralan':16,'ezil':16}}#animasyonların içerdiği resim sayısı.
    
    kare={'zombi1':{'öl':[],'saldır':[],'yürü':[],'yaralan':[],'ezil':[]},
          'zombi2':{'öl':[],'saldır':[],'yürü':[],'yaralan':[],'ezil':[]},
          'zombi3':{'öl':[],'saldır':[],'yürü':[],'yaralan':[],'ezil':[]},
          'zombi4':{'öl':[],'saldır':[],'yürü':[],'yaralan':[],'ezil':[]},
          'zombi5':{'öl':[],'saldır':[],'yürü':[],'yaralan':[],'ezil':[]},
          'zombi6':{'öl':[],'saldır':[],'yürü':[],'yaralan':[],'ezil':[]},}# animasyonların içerdiği resimler. ZipDosyaYukle fonksiyonunda yüklenecek
    
    atlasYuklendi={'zombi1':0,'zombi2':0,'zombi3':0,'zombi4':0,'zombi5':0,'zombi6':0} # atlas dosyalarının yüklenip yğklenmediğini kontrol edeceğimiz değişken. Yüklendiğine 1 olacak

    def __init__(self,tip,taraf,**kwargs):
        super().__init__(**kwargs)
        #Zombi nesnesi, oluşturulurduğunda sahnede görünmeyecek. Sırası geldiğine sahneye girecek. 
        #O yüzden boyut ve konumla ilgili ayarların kurucuda yapılmasına gerek yok.
        #Zombi nesnesi sahneye ekleneceği zaman yapılmalı

        self.tip=tip #'zombi1','zombi2','zombi3','zombi4','zombi5','zombi6'
        self.taraf=taraf # ekranın sol ya da sağ tarafında bulunabilir. 'sol','sağ'
        self.hiz=0 # ekranın genişliğine göre bir hız belirlenecek
        self.durum=''#'saldır','yürü','öl','yaralan','ezil'. SahneyeAyarla fonksiyonunda değer alacak
    
        self.kareSayac=0
        self.animasyonSaat=None

        self.canSayisi=Zombi.canlar[tip]
        self.canGosterge=CanGosterge(self) # zombinin kaç canı olduğunu gösterecek olan CanGosterge nesnesi
        self.sil=False #öldüğünde True olacak

        self.allow_stretch=True
        self.hiz=-1
  
    def SahneyeAyarla(self):
        #Zombi nesnesi, oluşturulurduğunda sahnede görünmeyecek. Sırası geldiğine sahneye girecek. 
        #O yüzden boyut ve konumla ilgili ayarların kurucuda yapılmasına gerek yok.
        #Zombi nesnesi sahneye ekleneceği zaman yapılmalı
        self.durum='yürü'
        self.BoyutAyarla()

        if self.taraf=='sol':
            self.yon='sağa'
            self.pos=[-self.width,Window.height*YKonumOran]
        elif self.taraf=='sağ':
            self.yon='sola'
            self.pos=[Window.width,Window.height*YKonumOran]

        self.HizHesapla()
        AciTersle(self)
        self.DurumDegistir(self.durum) 


    def AksiYoneGit(self):
        self.yonTersle()
        AciTersle(self)
        self.hizTersle()

    def hizTersle(self):
        self.hiz*=-1
    
    def yonTersle(self):
        if self.yon=='sola':
            self.yon='sağa'
        elif self.yon=='sağa':
            self.yon='sola'

    def BoyutAyarla(self):
        #resmin genişliğini, ekran genişliğine göre belirle. Sonra yüksekliği de aynı oranda hesapla
        #resimin hem genişliğinin hem yükseklğinin ayrı ayrı hesaplanması ve aynı zamanda genişlik/yükseklik oranının korunması gerekiyor
        self.width=Window.width*Zombi.genislikOran[self.tip]*Zombi.orijinalGenislik[self.durum][self.tip]/Zombi.orijinalGenislik['yürü'][self.tip]
        self.height=Zombi.orijinalYukseklik[self.durum][self.tip]*(self.width/Zombi.orijinalGenislik[self.durum][self.tip])#*Zombi.orijinalYukseklik[self.durum][self.tip]/Zombi.orijinalYukseklik['yürü'][self.tip]

        #canGosterge nesnesinin de boyutunun ayarlanması gerekiyor
        self.canGosterge.BoyutAyarla()

    def KonumAyarla(self):
        from sahne import Oyun #circular import : sahne modülünde, karakter modülü import edildiği için burada sahne modülünü sayfanın en üstünde import edemiyoruz
        self.x/=Oyun.EskiGenislik/Window.width
        self.y=Window.height*YKonumOran
        
    def HizHesapla(self):
        #zombinin hareket etme hızı, ekranın genişliğine göre ayarlanacak
        self.hiz=Window.width*Zombi.hizOran[self.tip]
        if self.yon=='sola':
            self.hizTersle()
    
    def TarafGuncelle(self):
        #zombi yürürken, ekranın bir tararından diğerine geçtiğinde çalışacak       
        if self.center_x>Window.width/2:
            self.taraf='sağ'
        if self.center_x<Window.width/2:
            self.taraf='sol'
        
    
    def Vuruldu(self):
        self.canSayisi-=1
        if self.canSayisi==0:
            self.DurumDegistir('öl')
        else:
            self.DurumDegistir('yaralan')
        #canGosterge işlemleri
        self.canGosterge.opacity=1
        self.canGosterge.DegerDegistir(self.canSayisi)
    
    def Ezildi(self):
        self.canSayisi-=1
        self.DurumDegistir('ezil')
        #canGosterge işlemleri
        self.canGosterge.opacity=1
        self.canGosterge.DegerDegistir(self.canSayisi)
            

        
    def DurumDegistir(self,durum):            
        self.durum=durum
        self.animasyonHazirlik()  


    def animasyonHazirlik(self):
        self.texture=Zombi.kare[self.tip][self.durum][0].texture#yeni durumun, ilk karesi alınıyor. Durum geçişinde, önceki durumun karesi kalmasın diye 
        self.BoyutAyarla()

        self.kareSayac=0
        if self.animasyonSaat:
            self.animasyonSaat.cancel()
        self.animasyonSaat=Clock.schedule_interval(self.animasyonTikTak,Zombi.gecikme[self.durum])
    
    def animasyonTikTak(self,dt):
        self.texture=Zombi.kare[self.tip][self.durum][self.kareSayac].texture
        self.kareSayac+=1
        if self.kareSayac==Zombi.kareSayisi[self.tip][self.durum]:  
            if self.durum=='yürü':
                self.kareSayac=0          
            elif self.durum=='öl':
                self.sil=True
                self.kareSayac=0 
            elif self.durum=='yaralan':
                self.DurumDegistir('yürü')
            elif self.durum=='ezil':
                if self.canSayisi==0:
                    self.DurumDegistir('öl')
                else:    
                    if (self.taraf=='sağ' and self.yon=='sola') or (self.taraf=='sol' and self.yon=='sağa'):
                        self.AksiYoneGit()
                    self.DurumDegistir('yürü')
            elif self.durum=='saldır':
                self.animasyonSaat.cancel()
                return


