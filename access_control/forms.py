from django import forms
from django.contrib.auth.models import User, Group
from django.apps import apps
from .models import AppPermission, UserAppPermission, GroupAppPermission, AccessLog

class AppPermissionForm(forms.ModelForm):
    class Meta:
        model = AppPermission
        fields = ['name', 'app_name', 'feature', 'permission_type', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get available apps for dropdown
        app_choices = [(app.name, app.verbose_name) for app in AppPermission.get_available_apps()]
        self.fields['app_name'] = forms.ChoiceField(choices=[('', '-- Select App --')] + app_choices)
        
        # Add Bootstrap classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class UserAppPermissionForm(forms.ModelForm):
    class Meta:
        model = UserAppPermission
        fields = ['user', 'permission']
    
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        # Only show active permissions
        self.fields['permission'].queryset = AppPermission.objects.filter(is_active=True)
        
        # Add Bootstrap classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Save the current user for later use in save method
        self.current_user = current_user
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.current_user:
            instance.granted_by = self.current_user
        if commit:
            instance.save()
        return instance

class GroupAppPermissionForm(forms.ModelForm):
    class Meta:
        model = GroupAppPermission
        fields = ['group', 'permission']
    
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        # Only show active permissions
        self.fields['permission'].queryset = AppPermission.objects.filter(is_active=True)
        
        # Add Bootstrap classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Save the current user for later use in save method
        self.current_user = current_user
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.current_user:
            instance.granted_by = self.current_user
        if commit:
            instance.save()
        return instance

class BulkPermissionForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    
    permissions = forms.ModelMultipleChoiceField(
        queryset=AppPermission.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        users = cleaned_data.get('users')
        groups = cleaned_data.get('groups')
        
        if not users and not groups:
            raise forms.ValidationError("You must select at least one user or group.")
        
        return cleaned_data

class PermissionRevokeForm(forms.Form):
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=UserAppPermission.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    
    group_permissions = forms.ModelMultipleChoiceField(
        queryset=GroupAppPermission.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['user_permissions'].queryset = UserAppPermission.objects.filter(user=user)
            self.fields.pop('group_permissions')
        elif group:
            self.fields['group_permissions'].queryset = GroupAppPermission.objects.filter(group=group)
            self.fields.pop('user_permissions')
        else:
            # If neither user nor group is provided, don't show any permissions
            self.fields['user_permissions'].queryset = UserAppPermission.objects.none()
            self.fields['group_permissions'].queryset = GroupAppPermission.objects.none() 