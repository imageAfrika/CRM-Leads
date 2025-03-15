from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Project, ProjectDocument, ProjectNote, ProjectMilestone
from .forms import (
    ProjectForm, ProjectDocumentForm, ProjectNoteForm,
    ProjectMilestoneForm, ProjectFilterForm
)

@login_required
def project_list(request):
    form = ProjectFilterForm(request.GET)
    projects = Project.objects.all()

    if form.is_valid():
        status = form.cleaned_data.get('status')
        priority = form.cleaned_data.get('priority')
        client = form.cleaned_data.get('client')
        manager = form.cleaned_data.get('manager')
        date_range = form.cleaned_data.get('date_range')
        search = form.cleaned_data.get('search')

        if status:
            projects = projects.filter(status=status)
        if priority:
            projects = projects.filter(priority=priority)
        if client:
            projects = projects.filter(client=client)
        if manager:
            projects = projects.filter(manager=manager)
        if search:
            projects = projects.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )
        
        if date_range:
            today = timezone.now().date()
            if date_range == 'today':
                projects = projects.filter(start_date=today)
            elif date_range == 'week':
                week_start = today - timedelta(days=today.weekday())
                projects = projects.filter(start_date__gte=week_start)
            elif date_range == 'month':
                projects = projects.filter(start_date__year=today.year, start_date__month=today.month)
            elif date_range == 'quarter':
                quarter_start = datetime(today.year, ((today.month-1)//3)*3+1, 1).date()
                projects = projects.filter(start_date__gte=quarter_start)
            elif date_range == 'year':
                projects = projects.filter(start_date__year=today.year)

    context = {
        'projects': projects,
        'form': form,
        'title': 'Projects'
    }
    return render(request, 'project_management/project_list.html', context)

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    documents = project.documents.all()
    notes = project.project_notes.all()
    milestones = project.milestones.all()
    
    # Calculate project metrics
    total_expenses = project.get_total_expenses()
    total_invoices = project.get_total_invoices()
    budget_utilization = project.get_budget_utilization()
    profit_margin = project.get_profit_margin()
    
    context = {
        'project': project,
        'documents': documents,
        'notes': notes,
        'milestones': milestones,
        'total_expenses': total_expenses,
        'total_invoices': total_invoices,
        'budget_utilization': budget_utilization,
        'profit_margin': profit_margin,
        'title': f'Project: {project.name}'
    }
    return render(request, 'project_management/project_detail.html', context)

@login_required
@permission_required('project_management.add_project', raise_exception=True)
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, 'Project created successfully.')
            return redirect('project_management:detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    return render(request, 'project_management/project_form.html', {
        'form': form,
        'title': 'Create Project'
    })

@login_required
@permission_required('project_management.change_project', raise_exception=True)
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('project_management:detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'project_management/project_form.html', {
        'form': form,
        'project': project,
        'title': f'Edit Project: {project.name}'
    })

@login_required
@permission_required('project_management.delete_project', raise_exception=True)
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully.')
        return redirect('project_management:list')
    return render(request, 'project_management/project_confirm_delete.html', {
        'project': project,
        'title': f'Delete Project: {project.name}'
    })

@login_required
def project_dashboard(request):
    # Get overall project statistics
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(status='in_progress').count()
    completed_projects = Project.objects.filter(status='completed').count()
    overdue_projects = Project.objects.filter(
        end_date__lt=timezone.now().date(),
        status__in=['planning', 'in_progress']
    ).count()

    # Get projects by status
    status_stats = Project.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')

    # Get projects by priority
    priority_stats = Project.objects.values('priority').annotate(
        count=Count('id')
    ).order_by('priority')

    # Get financial overview
    total_budget = Project.objects.aggregate(total=Sum('budget'))['total'] or 0
    total_actual_cost = Project.objects.aggregate(total=Sum('actual_cost'))['total'] or 0
    total_expenses = sum(project.get_total_expenses() for project in Project.objects.all())
    total_invoices = sum(project.get_total_invoices() for project in Project.objects.all())

    # Get recent projects
    recent_projects = Project.objects.order_by('-created_at')[:5]

    # Get upcoming milestones
    upcoming_milestones = ProjectMilestone.objects.filter(
        is_completed=False,
        due_date__gte=timezone.now().date()
    ).order_by('due_date')[:5]

    context = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'overdue_projects': overdue_projects,
        'status_stats': status_stats,
        'priority_stats': priority_stats,
        'total_budget': total_budget,
        'total_actual_cost': total_actual_cost,
        'total_expenses': total_expenses,
        'total_invoices': total_invoices,
        'recent_projects': recent_projects,
        'upcoming_milestones': upcoming_milestones,
        'title': 'Project Dashboard'
    }
    return render(request, 'project_management/project_dashboard.html', context)

# Document management views
@login_required
def document_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if request.method == 'POST':
        form = ProjectDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.project = project
            document.uploaded_by = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully.')
            return redirect('project_management:detail', pk=project_pk)
    else:
        form = ProjectDocumentForm()
    
    return render(request, 'project_management/document_form.html', {
        'form': form,
        'project': project,
        'title': 'Upload Document'
    })

@login_required
def document_delete(request, pk):
    document = get_object_or_404(ProjectDocument, pk=pk)
    project_pk = document.project.pk
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document deleted successfully.')
        return redirect('project_management:detail', pk=project_pk)
    return JsonResponse({'status': 'error'}, status=405)

# Note management views
@login_required
def note_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if request.method == 'POST':
        form = ProjectNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.project = project
            note.created_by = request.user
            note.save()
            messages.success(request, 'Note added successfully.')
            return redirect('project_management:detail', pk=project_pk)
    else:
        form = ProjectNoteForm()
    
    return render(request, 'project_management/note_form.html', {
        'form': form,
        'project': project,
        'title': 'Add Note'
    })

@login_required
def note_update(request, pk):
    note = get_object_or_404(ProjectNote, pk=pk)
    if request.method == 'POST':
        form = ProjectNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Note updated successfully.')
            return redirect('project_management:detail', pk=note.project.pk)
    else:
        form = ProjectNoteForm(instance=note)
    
    return render(request, 'project_management/note_form.html', {
        'form': form,
        'note': note,
        'project': note.project,
        'title': 'Edit Note'
    })

@login_required
def note_delete(request, pk):
    note = get_object_or_404(ProjectNote, pk=pk)
    project_pk = note.project.pk
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted successfully.')
        return redirect('project_management:detail', pk=project_pk)
    return JsonResponse({'status': 'error'}, status=405)

# Milestone management views
@login_required
def milestone_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if request.method == 'POST':
        form = ProjectMilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.project = project
            milestone.save()
            messages.success(request, 'Milestone added successfully.')
            return redirect('project_management:detail', pk=project_pk)
    else:
        form = ProjectMilestoneForm()
    
    return render(request, 'project_management/milestone_form.html', {
        'form': form,
        'project': project,
        'title': 'Add Milestone'
    })

@login_required
def milestone_update(request, pk):
    milestone = get_object_or_404(ProjectMilestone, pk=pk)
    if request.method == 'POST':
        form = ProjectMilestoneForm(request.POST, instance=milestone)
        if form.is_valid():
            form.save()
            messages.success(request, 'Milestone updated successfully.')
            return redirect('project_management:detail', pk=milestone.project.pk)
    else:
        form = ProjectMilestoneForm(instance=milestone)
    
    return render(request, 'project_management/milestone_form.html', {
        'form': form,
        'milestone': milestone,
        'project': milestone.project,
        'title': 'Edit Milestone'
    })

@login_required
def milestone_delete(request, pk):
    milestone = get_object_or_404(ProjectMilestone, pk=pk)
    project_pk = milestone.project.pk
    if request.method == 'POST':
        milestone.delete()
        messages.success(request, 'Milestone deleted successfully.')
        return redirect('project_management:detail', pk=project_pk)
    return JsonResponse({'status': 'error'}, status=405)

@login_required
def milestone_toggle(request, pk):
    milestone = get_object_or_404(ProjectMilestone, pk=pk)
    milestone.is_completed = not milestone.is_completed
    if milestone.is_completed:
        milestone.completed_date = timezone.now().date()
        milestone.completion_percentage = 100
    else:
        milestone.completed_date = None
    milestone.save()
    return JsonResponse({
        'status': 'success',
        'is_completed': milestone.is_completed,
        'completion_percentage': milestone.completion_percentage
    })
