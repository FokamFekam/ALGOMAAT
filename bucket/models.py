from django.db import models
from django.contrib.auth.models import User


from abstracts.models import Abstract
from contents.models import Publication, Space
from calendarapp.models import Event


class Bucket(Abstract):
     owner = models.ForeignKey(User, on_delete=models.CASCADE)


     def add_publication(self, user, publication):
     	 return None

class BucketOfContentsManager(models.Manager):
    def get_or_create(self, *args, **kwargs):
        owner=None
        try:
            contentsBucket = self.get(*args, **kwargs)
        except BucketOfContents.DoesNotExist:
            try:
                owner = kwargs["owner"]
            except KeyError:
                raise ObjectDoesNotExist
            if owner:
                return self.create(owner=owner)
        return contentsBucket

class BucketOfContents(Bucket):
    """ Users Bucket in wich he can organize contents
    """
   
    publications = models.ManyToManyField(Publication)
    
    objects = BucketOfContentsManager()

    def convert_to_space(self, title, is_private=True, delete=True):
        space =  Space.objects.create(title=title, is_private=is_private, owner=self.owner)
        for publication in self.publications.all():
             space.publications.add(publication)
        space.save()                           
        if delete:
            self.delete()
        return space
    
    def add_publication(self, user, publication):
        if publication.is_public_avail() or publication.is_in_user_space(user):
            self.publications.add(publication)
            return True
        return False
        
    def remove_publication(self, user, publication):
        if publication.is_public_avail() or publication.is_in_user_space(user):
            self.publications.remove(publication)
            return True
        return False
    
    def save(self, *args, **kwargs):
        """ This will assert that there is only one bucket per owner
        """
        try:
            contentsBucket =  BucketOfContents.objects.get(owner=self.owner)
        except  BucketOfContents.DoesNotExist:
            return super( BucketOfContents, self).save(*args, **kwargs)
        if self.id:
            for publication in self.publications:
                 contentsBucket.publications.add(publication)
        return  contentsBucket
        
        
        
 




class Inscription(Abstract):
	participant = models.ForeignKey(User,  on_delete=models.CASCADE)
	publication = models.ForeignKey(Publication,  on_delete=models.CASCADE)
	WAITING = 1
	CONFIRMED = 2
	CANCEL = 3
	TYPES_CHOICES = ( (WAITING, 'Waiting'),(CONFIRMED, 'Confirmed'),(CANCEL, 'Cancel') )
	status = models.IntegerField(TYPES_CHOICES, default=1)
	
	
	
	def check_publication_exist( self, publication_id ):
		publication = Publication.objects.filter(pk=publication_id)[0]
		if self.publication.id == publication.id:
			return True
		return False	
     
	"""
	def remove_publication(self, user, publication):
		if publication.is_public_avail() or publication.is_in_user_space(user):
			self.publications.remove(publication)
			return True
		return False

	  """





class BucketOfInscriptionsManager(models.Manager):
    def get_or_create(self, *args, **kwargs):
        owner=None
        try:
            inscriptionsBucket = self.get(*args, **kwargs)
        except BucketOfInscriptions.DoesNotExist:
            try:
                owner = kwargs["owner"]
            except KeyError:
                raise ObjectDoesNotExist
            if owner:
                return self.create(owner=owner)
        return inscriptionsBucket

   

class BucketOfInscriptions(Bucket):
	inscriptions = models.ManyToManyField(Inscription)
	objects = BucketOfInscriptionsManager()


	def add_publication(self, user, publication):
		return False
		
	def check_inscription_exist(self, pInscription):
		for inscription in self.inscriptions.all():
			if inscription.id == pInscription.id:
				return True
		return False
		
		
	def add_inscription(self, inscription):
		if not self.check_inscription_exist(inscription):
			self.inscriptions.add(publication)
			return True
		return False
		
	
	def remove_inscription(self, inscription):
		if self.inscriptions.all().count() > 0:
			self.inscriptions.remove(inscription)
			return True
		return False
	
       
       




class OrderManager(models.Manager):
    def get_or_create(self, *args, **kwargs):
        status=1
        buyer = None
        try:
            order = self.get(*args, **kwargs)
        except Order.DoesNotExist:
            try:
                buyer = kwargs["buyer"]
                status = kwargs["status"]
            except KeyError:
                raise ObjectDoesNotExist
            if buyer and status:
                return self.create(buyer=buyer, status=status)
        return order



class Order(Abstract): 
	buyer = models.ForeignKey(User,  on_delete=models.CASCADE)
	PENDING = 1	
	TOTAL_PAID = 2
	SEMI_PAID = 3	
	FAILED = 4
	TYPES_CHOICES = ( (PENDING, 'Pending'),(TOTAL_PAID, 'Total_Paid'),(SEMI_PAID, 'Partially_Paid'),(FAILED, 'Failed') )
	status = models.IntegerField(TYPES_CHOICES, default=1)
	total_amount = models.DecimalField(max_digits=8, decimal_places=2, default='00000.00')
	objects = OrderManager()
	



	  

class OrderInscription(models.Model):
	order = models.ForeignKey(Order,  on_delete=models.CASCADE)
	inscription = models.ForeignKey(Inscription,  on_delete=models.CASCADE)
    
    




	  

    

	      

