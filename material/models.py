from django.db import models
from django.contrib.auth.models import User
from abstracts.models import Abstract
from calendarapp.models import Event
from lessonapp.models import Question, Activity

# Create your models here.


#Debug
#from document.models import Document, Link, File
#ls=Link.objects.all()

# class DocumentManager(models.Manager):
#     def filter_with_score(self, *args, **kwargs):
#         qs = self.filter(*args, **kwargs).annotate(score=Sum('vote__rating'))
#         for a in qs:
#             if a.score == None:
#                 a.score = 0
#         return qs

class Document(Abstract):
    """ master class for urls/links, files, etc. 
        we will use djangos multi-table-inheritance
        to distingush the types
    """
    title = models.CharField(max_length=255)
       
    #objects = DocumentManager()
    
    def __unicode__(self):
        return "%s" % (self.title)
        
    def doc_type(self):
        return None

    def doc_link(self):
        return None

    def get_real_document(self):
        doc = None
        try:
            doc = self.link
        except self.DoesNotExist:
            pass
        try:
            doc = self.file
        except self.DoesNotExist:
            pass
        if doc:
            return doc
        else:
            raise self.DoesNotExist 
            
            



class Link(Document):
    url = models.URLField()
    
    def doc_type(self):
        return "L"

    def doc_link(self):
        return self.url

    def __unicode__(self):
        return "%s" % (self.url)



class File(Document):
    document = models.FileField(upload_to="files") #file is a internal command
    mime_type = models.CharField(max_length=255)
    hash_value = models.CharField(max_length=255) #hash is a internal command
    filename = models.CharField(max_length=255)
    size = models.PositiveIntegerField()
    
    
    def doc_type(self):
        return "F"

    def doc_link(self):
        return self.document.url
        
      





""" Material File and Link """
class Material(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    color = models.CharField(max_length=255, default="black")
    has_answer = models.BooleanField(default=False, blank=True)
    COURS = 1
    EXERCICE = 2
    REPONSE_EXERCICE = 3
    CORRECTION = 4
    TYPES_CHOICES = ( (COURS, 'COURS'), (EXERCICE, 'Exercice'), (REPONSE_EXERCICE, 'Ma Reponse'), (CORRECTION, 'correction') )
    m_type = models.IntegerField(TYPES_CHOICES, default=1)
    owner = models.ForeignKey(User,  on_delete=models.CASCADE, default=None)

    
    
    def doc_type(self):
        return self.document.get_real_document().doc_type()

    
      
    def doc_link(self):
        return self.document.get_real_document().doc_link()



class MaterialEventDoc(Material):
    events = models.ManyToManyField(Event)
	#event = models.ForeignKey(Event, on_delete=models.CASCADE)

	 
    
class MaterialQuestionDoc(Material):
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	


class MaterialActivityDoc(Material):
	activity = models.ForeignKey(Activity, on_delete=models.CASCADE)  
	

class MaterialResponseActivityDoc(Material):
	activity_doc = models.ForeignKey(MaterialActivityDoc, on_delete=models.CASCADE, default=None)  
	


        

""" Input box:  Checkbox  and Radio """
class InputBox(models.Model):
    title = models.CharField(max_length=255)
    color = models.CharField(max_length=255, default="black")
    is_answer = models.BooleanField(null=False,default=False)
    CHECKBOX = 1
    RADIO = 2
    TYPES_CHOICES = ((CHECKBOX, 'Checkbox'), (RADIO, 'Radio'))
    input_type = models.IntegerField(TYPES_CHOICES, default=2)
    
    


class InputQuestionBox(InputBox):
	question = models.ForeignKey(Question, on_delete=models.CASCADE)


class CheckedResponseInputQuestion(models.Model):
	input_question_box = models.ForeignKey(InputQuestionBox, on_delete=models.CASCADE)
	owner = models.ForeignKey(User,  on_delete=models.CASCADE, default=None)
	checked = models.PositiveIntegerField(default=0)




class Component(models.Model):
	title = models.CharField(max_length=255)
	color = models.CharField(max_length=255, default="black")
	is_answer = models.BooleanField(null=False,default=False)
	paragraph = models.TextField(null=True)
	img_width = models.IntegerField(default=400)
	img_height = models.IntegerField(default=300)
	image = models.ImageField(upload_to='img',null=True)
	number = models.IntegerField()
      
  
 
class ActivityComponent(Component):
	activity = models.ForeignKey(Activity, on_delete=models.CASCADE)  

 
 

    
        
  

