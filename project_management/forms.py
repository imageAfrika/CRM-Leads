from django import forms
from django.contrib.auth.models import User
from .models import Project, ProjectDocument, ProjectNote, ProjectMilestone

class ProjectForm(forms.ModelForm):
    team_members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        required=False
    )
    
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'})
    )
    
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
        required=False
    )

    class Meta:
        model = Project
        fields = [
            'name', 'code', 'description', 'client', 'start_date', 'end_date',
            'status', 'priority', 'budget', 'manager', 'team_members', 'tags'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'client': forms.Select(attrs={'class': 'form-control select2'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'manager': forms.Select(attrs={'class': 'form-control select2'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'data-role': 'tagsinput'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be earlier than start date.")

        return cleaned_data

class ProjectDocumentForm(forms.ModelForm):
    class Meta:
        model = ProjectDocument
        fields = ['title', 'document_type', 'file', 'description', 'version']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProjectNoteForm(forms.ModelForm):
    class Meta:
        model = ProjectNote
        fields = ['title', 'content', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ProjectMilestoneForm(forms.ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'})
    )
    
    completed_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
        required=False
    )

    class Meta:
        model = ProjectMilestone
        fields = ['title', 'description', 'due_date', 'completed_date', 'is_completed', 'completion_percentage']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'completion_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_completed = cleaned_data.get('is_completed')
        completion_percentage = cleaned_data.get('completion_percentage')
        completed_date = cleaned_data.get('completed_date')

        if is_completed and completion_percentage != 100:
            cleaned_data['completion_percentage'] = 100

        if is_completed and not completed_date:
            cleaned_data['completed_date'] = forms.DateField().clean(forms.DateField().to_python(None))

        return cleaned_data

class ProjectFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'All')] + Project.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    priority = forms.ChoiceField(
        choices=[('', 'All')] + Project.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    client = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Clients",
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    manager = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        empty_label="All Managers",
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    date_range = forms.ChoiceField(
        choices=[
            ('', 'All Time'),
            ('today', 'Today'),
            ('week', 'This Week'),
            ('month', 'This Month'),
            ('quarter', 'This Quarter'),
            ('year', 'This Year'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search projects...'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from clients.models import Client
        self.fields['client'].queryset = Client.objects.all() 