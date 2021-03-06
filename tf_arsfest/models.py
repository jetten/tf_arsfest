# --coding: UTF-8 --
from django.db import models
from referencenumber import viitenumeron_tarkiste

class Guest(models.Model):
    # Name
    name = models.CharField(max_length=90, verbose_name="Namn")
    
    # Email
    email = models.EmailField(verbose_name="E-post adress")
    
    # Phone
    phone = models.CharField(max_length=20, verbose_name="Telefonnummer")
    
    # Allergies
    allergies = models.CharField(max_length=180, verbose_name="Allergier/Dieter", blank=True)
    
    # Student or not
    type = models.ForeignKey('GuestType', verbose_name="Deltagartyp")

    # Sex
    SEX = (('M', 'Man'),('F', 'Kvinna'))
    sex = models.CharField(max_length=1, choices=SEX, verbose_name="Kön", blank=True)
    # Alkoholfri
    nonalcoholic = models.BooleanField(verbose_name="Alkoholfri", default=False)
    
    # Silliz
    silliz = models.BooleanField(verbose_name="Sillfrukost")
    
    event = models.ForeignKey('Event', verbose_name="Årsfest");
    
    def __unicode__(self):
        return self.name
    
        
class Registration(models.Model):
    
    # Vilken fest
    event = models.ForeignKey('Event', verbose_name="Årsfest");
    
    # Förening
    name = models.CharField(max_length=150, verbose_name="Förening/Post", blank=True, null=True)
    
    # Deltar i solenn-akt
    solennakt = models.BooleanField(verbose_name="Deltar i solenn akt", default=False)
    
    # Framför hälsning
    greeting = models.BooleanField(verbose_name="Vill framföra hälsning", default=False)
    
    # Gäst
    guest = models.OneToOneField(Guest, related_name="guest", unique=True)
    
    # Avec
    avec = models.OneToOneField(Guest, blank=True, null=True, related_name="avec", unique=True)
    
    # Övrigt
    misc = models.TextField(verbose_name="Övrigt", blank=True)
    
    # +1 boolean
    plusone = models.BooleanField(verbose_name="Lägg till person")
    
    # Avec boolean
    avecbutton = models.BooleanField(verbose_name="Avec")
    
    # Referensnummer till räkning
    reference_number = models.PositiveIntegerField(verbose_name="Referensnummer", blank=True, null=True, unique=True)
    
    # Summa på räkningen
    sum = models.FloatField(verbose_name="Summa", blank=True, null=True)
    
    def get_dictionary(self):
        
        data = {}
        
        registration = {}
        registration['org'] = self.name
        registration['solenn'] = "Ja" if self.solennakt else "Nej"
        registration['greeting'] = "Ja" if self.greeting else "Nej"
        registration['misc'] = self.misc
        data['registration'] = registration
        
        guest = {}
        guest['name'] = self.guest.name
        guest['email'] = self.guest.email
        guest['phone'] = self.guest.phone
        guest['allergies'] = self.guest.allergies
        guest['sex'] = self.guest.sex
        guest['type'] = unicode(self.guest.type)
        guest['nonalcoholic'] = "Ja" if self.guest.nonalcoholic else "Nej"
        guest['silliz'] = "Ja" if self.guest.silliz else "Nej"      
        data['guest'] = guest
        
        avec = {}
        if self.avec is not None:
            avec['name'] = self.avec.name
            avec['email'] = self.avec.email
            avec['phone'] = self.avec.phone
            avec['allergies'] = self.avec.allergies
            avec['sex'] = self.avec.sex
            avec['type'] = unicode(self.avec.type)
            avec['nonalcoholic'] = "Ja" if self.avec.nonalcoholic else "Nej"
            avec['silliz'] = "Ja" if self.avec.silliz else "Nej"
            data['avec'] = avec
            
        data['reference_number'] = self.reference_number
        data['sum'] = self.sum
        
        return data
    
    def save(self, *args, **kwargs):        
        self.sum = self.guest.type.price
        
        if self.avec is not None:
            self.sum += self.avec.type.price
            if self.avec.nonalcoholic and self.avec.type.price != 0:
                self.sum -= self.event.alcohol_price
            if self.avec.silliz:
                self.sum += self.event.silliz_price
            
            
        if self.guest.silliz:
            self.sum += self.event.silliz_price
            
        if self.guest.nonalcoholic and self.guest.type.price != 0:
            self.sum -= self.event.alcohol_price
        
        super(Registration, self).save(*args, **kwargs)
        
        if self.reference_number is None:
            pkey = "%d%d"%(self.event.year,self.pk)
            self.reference_number = "%d%d"%(int(pkey), viitenumeron_tarkiste(pkey))
            
        super(Registration, self).save(*args, **kwargs)
        
    
    
    
    def __unicode__(self):
        return "%s %s" % (self.name, self.guest.name)
    
class Event(models.Model):
    
    # Årsfest nr
    year = models.PositiveIntegerField(primary_key=True)
    
    # Date&Time
    date = models.DateTimeField()
    
    # Name
    name = models.CharField(max_length=120, verbose_name="Händelsens namn")
    
    # Platser
    places = models.PositiveIntegerField(verbose_name="Max antal gäster")
    
    # Anmälningen öppnar första gången
    round1_opens = models.DateTimeField()
    
    # Anmälningen stänger första gången
    round1_closes = models.DateTimeField()
    
    # Anmälningen öppnar andra gången
    round2_opens = models.DateTimeField()
    
    # Anmälningen stänger andra gången
    round2_closes = models.DateTimeField()
    
    # Beskrivning på anmälan
    registration_description = models.TextField(verbose_name="Beskrivning vid anmälan")    
    
    # Silliz pris
    silliz_price = models.PositiveIntegerField(verbose_name="Sillis pris")
    
    # Alkoholets pris
    alcohol_price = models.PositiveIntegerField(verbose_name="Hur mycket billigare är alkoholfritt?")
    
    def __unicode__(self):
        return self.name
    
class GuestType(models.Model):
    
    # Name of type
    name = models.CharField(max_length=50, verbose_name="Namn (t.ex. studerande)")
    
    # Price
    price = models.PositiveIntegerField(verbose_name="Pris")
    
    def __unicode__(self):
        return "%s (%de)" % (self.name, self.price)
    

