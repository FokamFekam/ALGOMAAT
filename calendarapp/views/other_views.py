# cal/views.py
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views import generic
from django.utils.safestring import mark_safe
from datetime import timedelta, datetime, date
import calendar
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from lessonapp.models import Theme
from calendarapp.models import EventMember, Event, Meeting, EventTheme
from calendarapp.utils import Calendar
from calendarapp.forms import EventForm, AddMemberForm , MeetingForm
from contents.models import Space, Publication
from bucket.models import Inscription
from material.models import File, Link,   Material, MaterialEventDoc, MaterialQuestionDoc
from material.forms import CreateMaterialFileForm, CreateMaterialLinkForm

def get_date(req_day):
	if req_day:
        	year, month = (int(x) for x in req_day.split("-"))
        	return date(year, month, day=1)
	return datetime.today()


def prev_month(d):
    	first = d.replace(day=1)
    	prev_month = first - timedelta(days=1)
    	month = "month=" + str(prev_month.year) + "-" + str(prev_month.month)
    	return month


def next_month(d):
    	days_in_month = calendar.monthrange(d.year, d.month)[1]
    	last = d.replace(day=days_in_month)
    	next_month = last + timedelta(days=1)
    	month = "month=" + str(next_month.year) + "-" + str(next_month.month)
    	return month


class CalendarView(LoginRequiredMixin, generic.ListView):
	login_url = "accounts:signin"
	model = Event
	template_name = "calendar.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		d = get_date(self.request.GET.get("month", None))
		cal = Calendar(d.year, d.month)
		html_cal = cal.formatmonth(withyear=True)
		context["calendar"] = mark_safe(html_cal)
		context["prev_month"] = prev_month(d)
		context["next_month"] = next_month(d)
		return context


@login_required(login_url="signup")
def create_event(request):
	form = EventForm(request.POST or None)
	if request.POST and form.is_valid():
		event = form.save()
		"""title = form.cleaned_data["title"]
		description = form.cleaned_data["description"]
		start_time = form.cleaned_data["start_time"]
		end_time = form.cleaned_data["end_time"]
		Event.objects.get_or_create(
		    user=request.user,
		    title=title,
		    description=description,
		    start_time=start_time,
		    end_time=end_time,
		)"""
		return HttpResponseRedirect(reverse("calendarapp:calendar"))
	return render(request, "calendarapp/event.html", {"form": form})



class EventEdit(generic.UpdateView):
	model = Event
	fields = ["title", "description", "start_time", "end_time"]
	template_name = "calendarapp/event.html"


@login_required(login_url="signup")
def update_meeting_link(request):
	if request.method == 'POST':
		event_id = request.POST.get('event_id')
		link_url = request.POST.get('link_url')
		meeting_id = request.POST.get('meeting_id')
		meeting = Meeting.objects.get(id=meeting_id)
		meeting.link_url = link_url
		meeting.save()
	return redirect("calendarapp:event-detail", event_id=event_id)
	
	



def check_event_saved(event, events_list):
	if not events_list:
		return False
	for event_item in events_list:
		if event.id == event_item["id"]:
			return True
	return False





def check_publication_saved(publication, publications_list):
	if not publications_list:
		return False
	for pub_item in publications_list:
		if publication.id == pub_item.id:
			return True
	return False






@login_required(login_url="signup")
def save_event_theme(request):
	if request.method == 'POST':
		event_id = request.POST.get('event_id')
		link_url = request.POST.get('link_url')
		theme_id = request.POST.get('theme_id')
		event = Event.objects.get(id=event_id)
		theme = Theme.objects.get(id=theme_id)
		
		if EventTheme.objects.filter(event=event, theme=theme).exists():
			event_theme = EventTheme.objects.filter(event=event, theme=theme).update(link_url=link_url);
			return JsonResponse({"success":True})
		else:
			event_theme = EventTheme.objects.create(event=event, theme=theme, link_url=link_url);
			return JsonResponse({"success":True})
			
		
	return JsonResponse({"success":False})





@login_required(login_url="signup")
def event_themes(request):
	if request.user.groups.filter(name='Simple_Customer').exists():
		inscriptions = Inscription.objects.filter(participant=request.user, status=2).order_by("created_at")
	else:
		inscriptions = Inscription.objects.filter(status=2).order_by("created_at")
		
		
	publications_list =[]
	results =[]
	for inscription in inscriptions:
		publication = inscription.publication
		if check_publication_saved(publication, publications_list) == False:
			publications_list.append(publication)
			events_list =[]
			for meeting in publication.meetings.all().order_by('-created_at'):
				event = meeting.event
				event_themes_list =[]
				if check_event_saved(event, events_list) == False:
					eventthemes = EventTheme.objects.filter(event=event)
					event_themes_list.append(eventthemes)
					event_dict = {
						"id"  : event.pk,
						"title": event.title,
						"start_time": event.start_time,
						"end_time": event.end_time,
						"eventthemes": event_themes_list,
					}
					events_list.append(event_dict)
			event_themes_dict = {
				"id"  : publication.pk,
				"title": publication.title,
				"price": publication.price,
				"events": events_list,
			}
			results.append(event_themes_dict)
	
	context = {"results": results }			
	return render(request, "calendarapp/event-themes.html", context)		
			

def remove_material_from_event(request, event_id, material_id):
	ct_json = {"success":False}
	event = get_object_or_404(Event, pk=event_id)
	material = get_object_or_404(MaterialEventDoc, pk=material_id)
	for evt in material.events.all():
		if event == evt:
			material.events.remove(event)
			ct_json =  {"success":True}
			return JsonResponse(ct_json)
	
	#return redirect(event.get_absolute_url())
	return JsonResponse(ct_json)


def add_material_to_event(request, event_id, material_id):
	ct_json = {"success":False}
	event = get_object_or_404(Event, pk=event_id)
	material = get_object_or_404(MaterialEventDoc, pk=material_id) 
	for evt in material.events.all():
		if event == evt:
			return JsonResponse(ct_json)
	
	material.events.add(event)
	ct_json =  {"success":True}
	#return redirect(event.get_absolute_url())
	return JsonResponse(ct_json)
	




def ajax_get_materials(request): 
	materials = MaterialEventDoc.objects.filter(owner=request.user)	
	materials_results = []
	for material in materials:
		response_data = {}
		response_data['id'] = material.id
		response_data['title'] = material.title
		response_data['description'] = material.description
		#response_data['document'] = material.document
		response_data['has_answer'] = material.has_answer
		response_data['m_type'] = material.m_type
		response_data['owner'] = material.owner.username

		materials_results.append(response_data)
	return JsonResponse(materials_results, safe=False)
	



@login_required(login_url="signup")
def event_details(request, event_id):
	event = Event.objects.get(id=event_id)
	eventmember = EventMember.objects.filter(event=event)
	member_count = eventmember.count()
	eventthemes = EventTheme.objects.filter(event=event)
	
	#materials = MaterialEventDoc.objects.filter(event=event_id)
	materials = event.materialeventdoc_set.all()

	meetings = Meeting.objects.filter(event=event)
	publications_list =[]
	for meeting in meetings:
		publications = meeting.publication_set.all()
		#check if publication already saved in publications_list
		for publication in publications:
			if check_publication_saved(publication, publications_list) == False:
				publications_list.append(publication)
	
	
	users_list = []	
	for publication in publications_list:
		inscriptions = Inscription.objects.filter(publication=publication, status=2)	
		for inscription in inscriptions:
			users_list.append(inscription.participant)		
		
					
	
	forms_member = AddMemberForm()
	form_file = CreateMaterialFileForm(user=request.user, event_id=event_id, nodetype_id=11)
	form_link = CreateMaterialLinkForm(user=request.user, event_id=event_id, nodetype_id=11)
	context = {"event": event, "eventmember": eventmember, "eventthemes": eventthemes, "materials": materials, "meetings": meetings, "users":users_list, "form_member":forms_member, "form_file":form_file, "form_link":form_link}
	return render(request, "calendarapp/event-details.html", context)




@login_required
def create_file(request, event_id=None, nodetype_id=11):
    if request.method == 'POST':
        form = CreateMaterialFileForm(request.POST, request.FILES, user=request.user, event_id=event_id, nodetype_id=nodetype_id)
        if form.is_valid():
            material = form.save()
            event = get_object_or_404(Event, pk=event_id)
            return redirect(event.get_absolute_url())
           
            
    else:
        form = CreateMaterialFileForm(user=request.user, event_id=event_id, nodetype_id=nodetype_id)
    context_dict = {"form": form , "event_id":event_id, "nodetype_id":nodetype_id}
    template="materials/new_file_material.html"
    return render(request, template, context_dict)
    
    
    
@login_required
def create_link(request, event_id=None, nodetype_id=11):
    if request.method == 'POST':
        form = CreateMaterialLinkForm(request.POST, request.FILES, user=request.user, event_id=event_id, nodetype_id=nodetype_id)
        if form.is_valid():
            material = form.save()
            event = get_object_or_404(Event, pk=event_id)
            return redirect(event.get_absolute_url())
           
            
    else:
        form = CreateMaterialLinkForm(user=request.user, event_id=event_id, nodetype_id=nodetype_id)
    context_dict = {"form": form , "event_id":event_id, "nodetype_id":nodetype_id}
    template="materials/new_file_material.html"
    return render(request, template, context_dict)
  
    



def add_eventmember(request, event_id):
	forms = AddMemberForm()
	if request.method == "POST":
		forms = AddMemberForm(request.POST)
		if forms.is_valid():
		    member = EventMember.objects.filter(event=event_id)
		    event = Event.objects.get(id=event_id)
		    if member.count() <= 9:
		        user = forms.cleaned_data["user"]
		        is_added = forms.cleaned_data["is_added"]
		        EventMember.objects.create(event=event, user=user, is_added=is_added)
		        return redirect('calendarapp:event-detail', event_id=event_id)  
		    else:
		        print("--------------User limit exceed!-----------------")
	context = {"form": forms}
	return render(request, "calendarapp/add_member.html", context)


class EventMemberDeleteView(generic.DeleteView):
	model = EventMember
	template_name = "event_delete.html"
	success_url = reverse_lazy("calendarapp:calendar")

class CalendarViewNew(LoginRequiredMixin, generic.View):
	login_url = "accounts:signin"
	template_name = "calendarapp/calendar.html"
	form_class = EventForm
	def check_event_exists(self, event_list, event_id):
		for event in event_list:
			if event["id"] == event_id:
				return True
		return False
		
	def get(self, request, *args, **kwargs):
		forms = self.form_class(user=request.user)
		
		event_list = []
		# add events from my inscriptions
		inscriptions = Inscription.objects.filter(participant=request.user, status=2)
		for inscription in inscriptions:
			print(inscription.publication)
			for meeting in inscription.publication.meetings.all():
				event = meeting.event
				#check if this event already saved in event_list
				if self.check_event_exists(event_list, event.id) == False:
					event_list.append(
						{   "id": event.id,
						    "title": event.title,
						    "start": event.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
						    "end": event.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
						    "description": event.description,
						}
					)  
				
			
					
		# add events created by user		
		events_month = Event.objects.get_running_events(user=request.user)
		events = Event.objects.get_all_events(user=request.user)
		#event_list = []
		# start: '2020-09-16T16:00:00'
		for event in events:
		    #check if this event already saved in event_list
		    if self.check_event_exists(event_list, event.id) == False:
			    event_list.append(
				{   "id": event.id,
				    "title": event.title,
				    "start": event.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
				    "end": event.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
				    "description": event.description,
				}
			    ) 
		
		
		is_simple_customer = request.user.groups.filter(name='Simple_Customer').exists()
		context = {"form": forms, "events": event_list,
		           "events_month": events_month, "is_simple_customer":is_simple_customer}
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		forms = self.form_class(request.POST , user=request.user )
		if forms.is_valid():
		    form = forms.save()
		    #form.user = request.user
		    #form.save()
		    return redirect("calendarapp:calendar")
		context = {"form": forms}
		return render(request, self.template_name, context)



def delete_event(request, event_id):
	event = get_object_or_404(Event, id=event_id)
	if request.method == 'POST':
		event.delete()
		return JsonResponse({'message': 'Event sucess delete.'})
	else:
		return JsonResponse({'message': 'Error!'}, status=400)




def clone_meeting_and_update_pub(event_id, cloned_event):
	event = get_object_or_404(Event, id=event_id)
	print(event)
	meetings = Meeting.objects.filter(event=event)
	publications_from = Publication.objects.filter(meetings__in=meetings).distinct()
	for meeting in meetings:
		for publication in publications_from:
			print("373----revoir cloned meeting---")
			print(cloned_event)
			cloned_meeting =  Meeting.objects.create(m_type=meeting.m_type, event = cloned_event,  is_active=meeting.is_active)
			#meeting.get_cloned_meeting(cloned_event)
			publication.meetings.add(cloned_meeting)



def next_week(request, event_id):
	event = get_object_or_404(Event, id=event_id)
	if request.method == 'POST':
		next = event
		next.id = None
		next.start_time += timedelta(days=7)
		next.end_time += timedelta(days=7)
		next.save()		
		#get cloned meeting with next and update pubications
		clone_meeting_and_update_pub(event_id, next)
		return JsonResponse({'message': 'Sucess!'})
	else:
        	return JsonResponse({'message': 'Error!'}, status=400)

def next_day(request, event_id):
	event = get_object_or_404(Event, id=event_id)
	if request.method == 'POST':
		next = event
		next.id = None
		next.start_time += timedelta(days=1)
		next.end_time += timedelta(days=1)
		next.save()
		#get cloned meeting with next and update pubications
		clone_meeting_and_update_pub(event_id, next)
		return JsonResponse({'message': 'Sucess!'})
	else:
		return JsonResponse({'message': 'Error!'}, status=400)


def event_all_weeks(request):
	if request.method == 'POST':
		from_date = request.POST.get('from_date')
		to_date = request.POST.get('to_date')
		event_id = request.POST.get('eventId_to_repeat')
		event = get_object_or_404(Event, id=event_id)
		from_next_week_date  = event.start_time
		to_next_week_date  = event.end_time
		from_next_week_date2  = event.start_time.strftime('%Y-%m-%d')
		to_next_week_date2  = event.end_time.strftime('%Y-%m-%d')
		to_date = datetime.strptime(to_date.split("T")[0], '%Y-%m-%d').strftime('%Y-%m-%d')
		from_date = datetime.strptime(from_date.split("T")[0], '%Y-%m-%d').strftime('%Y-%m-%d')
		if to_date >= from_date and (to_next_week_date2 >= from_next_week_date2)  and ((to_next_week_date + timedelta(days=7)).strftime('%Y-%m-%d') <= to_date):
			#meetings_from = Meeting.objects.filter(event=event)
			#publications_from = Publication.objects.filter(meetings__in=meetings_from).distinct()
			while (to_next_week_date + timedelta(days=7)).strftime('%Y-%m-%d') <= to_date:
				next = event
				next.id = None
				next.start_time = from_next_week_date + timedelta(days=7)
				next.end_time = to_next_week_date + timedelta(days=7)
				next.save()
				clone_meeting_and_update_pub(event_id, next)
				#for meeting in meetings_from:
					#for publication in publications_from:
						#cloned_meeting = meeting.get_cloned_meeting(next)
						#publication.meetings.add(cloned_meeting)
				from_next_week_date  += timedelta(days=7)
				to_next_week_date  += timedelta(days=7)
				from_next_week_date2  = from_next_week_date.strftime('%Y-%m-%d')
				to_next_week_date2  = to_next_week_date.strftime('%Y-%m-%d')
			
	return redirect("calendarapp:calendar")
        
        
        
def add_meeting(request, publication_id):
	
	if request.method == "POST":
		form = MeetingForm(request.POST, publication_id=publication_id)
		if form.is_valid():
        		meeting = form.save()
        	
	else:
		form = MeetingForm(publication_id = publication_id)
	context_dict = {"form": form}
	return render(request, "calendarapp/add_meeting.html", context_dict)
