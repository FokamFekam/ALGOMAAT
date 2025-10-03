from django.forms import ModelForm, DateInput
from calendarapp.models import Event, EventMember, Meeting 
from contents.models import Publication, Space
from django import forms
from django.forms.widgets import CheckboxSelectMultiple



class EventForm(ModelForm):
	class Meta:
		model = Event
		fields = ["title", "description", "start_time", "end_time"]
		# datetime-local is a HTML5 input type
		widgets = {
			"title": forms.TextInput(
		        	attrs={"class": "form-control", "placeholder": "Enter event title"}
		    	),
		    	"description": forms.Textarea(
		        	attrs={
		            		"class": "form-control",
		            		"placeholder": "Enter event description",
		        	}
		    	),
		    	"start_time": DateInput(
		        	attrs={"type": "datetime-local", "class": "form-control"},
		        	format="%Y-%m-%dT%H:%M",
		    	),
		    	"end_time": DateInput(
		        	attrs={"type": "datetime-local", "class": "form-control"},
		        	format="%Y-%m-%dT%H:%M",
		    	),
		}
		exclude = ["user"]

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		super(EventForm, self).__init__(*args, **kwargs)
		self.fields["start_time"].input_formats = ("%Y-%m-%dT%H:%M",)
		self.fields["end_time"].input_formats = ("%Y-%m-%dT%H:%M",)	
		self.fields['meetings'] = forms.MultipleChoiceField(
			required=False, 
			label='meetings',
	       	widget=CheckboxSelectMultiple(), 
	       	choices=Meeting.TYPES_CHOICES  
	        )
		self.fields['publications'] = forms.ModelMultipleChoiceField(
	       	queryset = Publication.objects.filter(spaces__owner=self.user).distinct(),
			required=False, 
			label='meetings',
	       	#widget=FilteredSelectMultiple("publications", is_stacked=False)
	       	widget=forms.SelectMultiple()
	        )
			
	def save(self):
		data = self.cleaned_data
		event = Event.objects.create(title=data["title"], description=data["description"], start_time=data["start_time"], 				end_time=data["end_time"], user=self.user )
		#publications = Publication.objects.filter(spaces__owner=self.user)
		for meeting2 in data["meetings"]:
			meeting =  Meeting.objects.create(m_type=meeting2, event = event, is_active=True)
			for publication in data["publications"]:
				publication.meetings.add(meeting)
				publication.save()		
							
		return event		




class AddMemberForm(forms.ModelForm):
	class Meta:
        	model = EventMember
        	fields = ["user", "is_added"]
        
 
        
class MeetingForm(forms.ModelForm):
	class Meta:
		model = Meeting
		fields = ["m_type"]
        
	def __init__(self, *args, **kwargs):
		publication_id = kwargs.pop('publication_id')	
		#publication = Publication.objects.filter(pk=publication_id)
		self.publication_id = publication_id   
		event_id = kwargs.pop('event_id')
		self.event_id = event_id	             
		super(MeetingForm, self).__init__(*args, **kwargs)
		
	def save(self):
		data = self.cleaned_data
		publication = Publication.objects.get(pk=self.publication_id)
		event = Event.objects.get(pk=self.event_id)
		""" This will assert that there is only one default meeting per m_type and per publication
		"""
		meeting =  Meeting.objects.create(m_type=data["m_type"], event = event,  is_active=True)
		meeting.save()
		publication.meetings.add(meeting)
		#publication.save()
		return meeting
		
        
   



