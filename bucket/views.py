from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponse, JsonResponse
import json as simplejson
from django.core import serializers
from django.contrib.auth.models import User
from .models import BucketOfContents, BucketOfInscriptions, Inscription, Order, OrderInscription
from contents.models import Publication, Space
from bucket.serializers import BucketOfContentsSerializer, InscriptionSerializer
from contents.serializers import PublicationSerializer
import decimal
from django.db.models import Q



JSON_DICT = {"success":True}
JSON_DICT_FALSE = {"success":False}



def bucket(request, template="bucket.html"):
    #bucket = BucketOfContents.objects.get_or_create(owner=request.user)
    #context_dict = {"bucket":bucket}
    return render(request, 'bucket/bucket.html', { })

def cart(request, template="cart.html"):
    bucket = BucketOfInscriptions.objects.get_or_create(owner=request.user)
    inscriptions = bucket.inscriptions.all()
    context_dict = {"order":0}
    if inscriptions.count() > 0:
    	orderInscription = OrderInscription.objects.get(inscription=inscriptions[0])
    	context_dict = {"order":orderInscription.order}
    
    return render(request, 'bucket/cart.html', context_dict )
    
def ajax_get_contents_data(request):
    bucket = BucketOfContents.objects.filter(owner=request.user)
    results = BucketOfContentsSerializer(bucket, many=True).data
    return JsonResponse(results, safe=False)
    

def ajax_get_cart_data(request):
	bucket = BucketOfInscriptions.objects.get_or_create(owner=request.user)
	
	inscriptions_dict = {}
	inscriptions_dicts = []
   
	
	#inscriptions = Inscription.objects.filter(order=order, status=1).order_by("participant")
	for inscription in bucket.inscriptions.all():
		publication_dict = {
			"id": inscription.publication.id,
			"title": inscription.publication.title,
			"description": inscription.publication.description,
			"price": inscription.publication.price,
			"is_private": inscription.publication.is_private,			
			
		}
			#publications_dicts.append(PublicationSerializer(inscription.publication, many=True).data)
		user = inscription.participant
			
		inscriptions_dict = {
			"id"  : inscription.pk,
			"participant": user.pk,
			"participant_name": user.username,
			"publications": [publication_dict],
			}
		# check if this inscription was already saved inside inscriptions_dicts
		itemFound = False
		for item in inscriptions_dicts:
			if item["participant"] == inscriptions_dict["participant"]:
				item["publications"].append(publication_dict)
				itemFound = True
		if itemFound == False:
			inscriptions_dicts.append(inscriptions_dict)
				
			
  
	#print(inscriptions_dicts)
	return JsonResponse(inscriptions_dicts, safe=False)
    

def add_publication_to_bucket(request, publication_id):
    bucket = BucketOfContents.objects.get_or_create(owner=request.user)
    publication = get_object_or_404(Publication, pk=publication_id)
    bucket.add_publication(request.user, publication)
    ct_json = JSON_DICT
    return JsonResponse(ct_json)


    



def add_or_create_inscription2(participant_id, publication_id):
	foundUser = User.objects.get(id=participant_id)
	publication = Publication.objects.filter(pk=publication_id)[0]
	if Inscription.objects.filter(participant=foundUser, status=1, publication=publication).exists():
		inscription = Inscription.objects.get(participant=foundUser, publication=publication)

	else:	
		inscription = Inscription.objects.create(participant=foundUser, status=1, publication=publication)
	return inscription


def check_inscription_exist(request, participant_id, publication_id):
	#bucket = BucketOfInscriptions.objects.get_or_create(owner=request.user)
	foundUser = User.objects.get(id=int(participant_id))
	publication = Publication.objects.filter(pk=publication_id)[0]
	ct_json_false = JSON_DICT_FALSE
	ct_json = JSON_DICT
	if Inscription.objects.filter(participant=foundUser, status=1, publication=publication).exists():
		inscription = Inscription.objects.get(participant=foundUser, status=1, publication=publication)
		print(inscription)
		return JsonResponse(ct_json)
									
	else:	
		print("119")	
		return JsonResponse(ct_json_false)
	return JsonResponse(ct_json_false)
		



def add_inscription_into_order(request, bucket, inscription, order):	
	if not OrderInscription.objects.filter(order=order, inscription=inscription).exists():
		bucket.inscriptions.add(inscription)
		order.total_amount = decimal.Decimal(order.total_amount) + decimal.Decimal(inscription.publication.price)
		order.save()
		OrderInscription.objects.create(order=order, inscription=inscription)
	
			
	
# call just add_or_create_inscription(participant_name, publication, bucket, user)
def add_publications_to_bucket_of_inscriptions(request):
	if request.method == 'POST':
		bucket = BucketOfInscriptions.objects.get_or_create(owner=request.user)
		order = Order.objects.get_or_create(buyer=request.user, status=1)
				
		publication_id = request.POST.get('publication_id')
		number_of_participants = request.POST.get('index')
		for index in range(1, int(number_of_participants) + 1):
			user_name = str(request.POST.get('participant_name_'+ str(index)))
			user_id = request.POST.get('participantId_'+ str(index))
			if int(publication_id) != int(0) :
				publication = Publication.objects.filter(pk=publication_id)[0]
				inscription = add_or_create_inscription2(user_id, publication_id)
				add_inscription_into_order(request, bucket, inscription, order)
				
			else:
				space = Space.objects.filter(pk=space_id)[0]
				for publication in space.get_publications():
					if not publication.is_private:
						inscription = add_or_create_inscription2(user_id, publication_id)
						add_inscription_into_order(request, bucket, inscription, order)
				
		ct_json = JSON_DICT
	return JsonResponse(ct_json)

def remove_publication_from_bucket(request, publication_id):
    bucket = BucketOfContents.objects.get_or_create(owner=request.user)
    publication = get_object_or_404(Publication, pk=publication_id)
    bucket.remove_publication(request.user, publication)
    ct_json = JSON_DICT
    return JsonResponse(ct_json)
    
def remove_inscription_from_bucket(request, inscription_id):
    bucket = BucketOfInscriptions.objects.get_or_create(owner=request.user)
    inscription = get_object_or_404(Inscription, pk=inscription_id)
    bucket.remove_inscription(inscription)
    
    
    if OrderInscription.objects.filter(inscription=inscription).exists():
    	orderInscription = OrderInscription.objects.get(inscription=inscription)
    	order = orderInscription.order    
    	orderInscription.delete()
    
    	inscription.delete()
    	if not OrderInscription.objects.filter(order=order).exists():
    		order.delete()
    	else:
    		order.total_amount = decimal.Decimal(order.total_amount) - decimal.Decimal(inscription.publication.price)
    		order.save()
     
    ct_json = JSON_DICT
    return JsonResponse(ct_json)
    

 
   
  
      
 
@login_required(login_url="/users/login/")
def convert_to_space(request):
    # # # BAD BAD BAD ASS fast and hacky #TODO
    if request.method == 'POST':
        title = request.POST.get('title2', "None")
        is_private = request.POST.get('is_private2', False)
        bucket = BucketOfContents.objects.get_or_create(owner=request.user)
        space = bucket.convert_to_space(title, is_private, True)
    return redirect("contents:private_spaces", private=False)
    
 



