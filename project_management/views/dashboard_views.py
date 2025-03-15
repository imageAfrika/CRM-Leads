from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum, Count
from django.utils import timezone
from ..models import Project, ProjectMilestone

@login_required
@permission_required('project_management.view_project_dashboard', raise_exception=True)
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

    # Calculate project performance metrics
    total_profit = total_invoices - total_expenses
    profit_margin = (total_profit / total_invoices * 100) if total_invoices > 0 else 0
    budget_utilization = (total_actual_cost / total_budget * 100) if total_budget > 0 else 0
    completion_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0

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
        'total_profit': total_profit,
        'profit_margin': profit_margin,
        'budget_utilization': budget_utilization,
        'completion_rate': completion_rate,
        'recent_projects': recent_projects,
        'upcoming_milestones': upcoming_milestones,
        'title': 'Project Dashboard'
    }
    return render(request, 'project_management/project_dashboard.html', context)

@login_required
@permission_required('project_management.view_project_analytics', raise_exception=True)
def project_analytics(request):
    # Get project completion trends
    completion_trend = Project.objects.filter(
        status='completed'
    ).values('end_date__month').annotate(
        count=Count('id')
    ).order_by('end_date__month')

    # Get budget vs actual cost comparison
    budget_vs_actual = Project.objects.values('name').annotate(
        budget=Sum('budget'),
        actual=Sum('actual_cost')
    ).filter(budget__isnull=False, actual_cost__isnull=False)

    # Get project status distribution
    status_distribution = Project.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')

    # Get priority distribution
    priority_distribution = Project.objects.values('priority').annotate(
        count=Count('id')
    ).order_by('priority')

    # Get client project distribution
    client_distribution = Project.objects.values('client__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    # Get team member workload
    team_workload = Project.objects.filter(
        status='in_progress'
    ).values('team_members__username').annotate(
        count=Count('id')
    ).order_by('-count')

    context = {
        'completion_trend': completion_trend,
        'budget_vs_actual': budget_vs_actual,
        'status_distribution': status_distribution,
        'priority_distribution': priority_distribution,
        'client_distribution': client_distribution,
        'team_workload': team_workload,
        'title': 'Project Analytics'
    }
    return render(request, 'project_management/project_analytics.html', context) 