from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django_filters.views import FilterView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .filters import ApplicationFilter
import csv
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import io
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.db.models import Count, Avg, Q, F, FloatField, DurationField, ExpressionWrapper
from .models import Program, Application, ApplicationDocument, NotificationPreference, ApplicationStatus
from .forms import ApplicationForm, ApplicationDocumentForm, ApplicationReviewForm
from .utils import send_application_status_update


class ProgramListView(ListView):
    model = Program
    template_name = 'applications/program_list.html'
    context_object_name = 'programs'
    
    def get_queryset(self):
        return Program.objects.filter(is_active=True, end_date__gte=timezone.now())

class ProgramDetailView(DetailView):
    model = Program
    template_name = 'applications/program_detail.html'
    context_object_name = 'program'

# @login_required
# def application_create(request, program_id):
#     program = get_object_or_404(Program, pk=program_id)
    
#     # Check if user already has an application for this program
#     existing_application = Application.objects.filter(
#         program=program,
#         applicant=request.user
#     ).first()
    
#     if existing_application:
#         messages.warning(request, 'You have already applied for this program.')
#         return redirect('applications:application_detail', pk=existing_application.pk)
    
#     if request.method == 'POST':
#         form = ApplicationForm(program, request.POST)
#         document_form = ApplicationDocumentForm(request.POST, request.FILES)
        
#         if form.is_valid() and document_form.is_valid():
#             application = form.save(commit=False)
#             application.program = program
#             application.applicant = request.user
#             application.status = 'submitted'
#             application.submitted_at = timezone.now()
#             application.save()
            
#             if document_form.cleaned_data.get('document'):
#                 document = document_form.save(commit=False)
#                 document.application = application
#                 document.save()
            
#             messages.success(request, 'Your application has been submitted successfully.')
#             return redirect('applications:application_detail', pk=application.pk)
#     else:
#         form = ApplicationForm(program)
#         document_form = ApplicationDocumentForm()
    
#     return render(request, 'applications/application_form.html', {
#         'form': form,
#         'document_form': document_form,
#         'program': program
#     })


class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = Application
    template_name = 'applications/application_form.html'
    form_class = ApplicationForm
    login_url = '/login/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.program = get_object_or_404(Program, pk=self.kwargs['program_id'])
        kwargs['program'] = self.program
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['program'] = self.program
        return context

    def form_valid(self, form):
        form.instance.applicant = self.request.user
        form.instance.program = self.program
        form.instance.status = 'submitted'
        form.instance.submitted_at = timezone.now()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('applications:application_detail', kwargs={'pk': self.object.pk})

        

@login_required
def application_detail(request, pk):
    application = get_object_or_404(Application, pk=pk)
    if not (request.user == application.applicant or request.user.is_staff):
        messages.error(request, 'You do not have permission to view this application.')
        return redirect('applications:program_list')
    
    return render(request, 'applications/application_detail.html', {
        'application': application
    })

class ApplicationListView(LoginRequiredMixin, ListView):
    model = Application
    template_name = 'applications/application_list.html'
    context_object_name = 'applications'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Application.objects.all()
        return Application.objects.filter(applicant=self.request.user)

@login_required
def application_review(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to review applications.')
        return redirect('applications:program_list')
    
    application = get_object_or_404(Application, pk=pk)
    old_status = application.status
    
    if request.method == 'POST':
        form = ApplicationReviewForm(request.POST, instance=application)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewed_by = request.user
            review.save()
            
            # Send email notification if status has changed
            if old_status != review.status:
                send_application_status_update(review)
            
            messages.success(request, 'Application review has been saved.')
            return redirect('applications:application_detail', pk=application.pk)
    else:
        form = ApplicationReviewForm(instance=application)
    
    return render(request, 'applications/application_review.html', {
        'form': form,
        'application': application
    })



class DashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'applications/dashboard.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get overall statistics
        context['total_applications'] = Application.objects.count()
        context['pending_applications'] = Application.objects.filter(
            status__in=['submitted', 'under_review']
        ).count()
        
        # Get program-wise statistics
        context['program_stats'] = Program.objects.annotate(
            total_applications=Count('application'),
            pending_applications=Count('application', 
                filter=Q(application__status__in=['submitted', 'under_review'])),
            approved_applications=Count('application', 
                filter=Q(application__status='approved')),
            rejected_applications=Count('application', 
                filter=Q(application__status='rejected'))
        )
        
        # Get recent applications
        context['recent_applications'] = Application.objects.select_related(
            'program', 'applicant'
        ).order_by('-submitted_at')[:10]
        
        return context

    
class ApplicationListView(LoginRequiredMixin, FilterView):
    model = Application
    template_name = 'applications/application_list.html'
    context_object_name = 'applications'
    filterset_class = ApplicationFilter
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(applicant=self.request.user)
        
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(program__name__icontains=search_query) |
                Q(applicant__first_name__icontains=search_query) |
                Q(applicant__last_name__icontains=search_query)
            )
        return queryset



@login_required
def export_applications(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to export applications.')
        return redirect('applications:application_list')

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    export_format = request.GET.get('format', 'csv')

    applications = Application.objects.select_related(
        'program', 'applicant', 'reviewed_by'
    )

    if date_from and date_to:
        applications = applications.filter(
            submitted_at__date__range=[date_from, date_to]
        )

    data = [['Program', 'Applicant', 'Status', 'Submitted Date', 'Review Notes', 'Reviewed By']]
    for app in applications:
        data.append([
            app.program.name,
            app.applicant.get_full_name(),
            app.get_status_display(),
            app.submitted_at.strftime('%Y-%m-%d'),
            app.review_notes or '',
            app.reviewed_by.get_full_name() if app.reviewed_by else ''
        ])

    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        filename = f'applications_{date_from}_{date_to}.csv' if date_from and date_to else 'applications.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        writer.writerows(data)
        
        return response

    elif export_format == 'excel':
        wb = Workbook()
        ws = wb.active
        ws.title = "Applications"
        
        for row in data:
            ws.append(row)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = f'applications_{date_from}_{date_to}.xlsx' if date_from and date_to else 'applications.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        wb.save(response)
        return response

    elif export_format == 'pdf':
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        
        doc.build(elements)
        
        response = HttpResponse(content_type='application/pdf')
        filename = f'applications_{date_from}_{date_to}.pdf' if date_from and date_to else 'applications.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        
        return response

    return HttpResponse('Invalid export format specified.', status=400)  


@login_required
def bulk_application_review(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('applications:application_list')

    application_ids = request.POST.getlist('application_ids')
    action = request.POST.get('action')
    
    # Map action to correct status
    status_map = {
        'approve': 'approved',
        'reject': 'rejected',
        'review': 'under_review'
    }
    status = status_map.get(action, action)

    applications = Application.objects.filter(id__in=application_ids)
    
    for application in applications:
        application.status = status
        application.save()
        
        ApplicationStatus.objects.create(
            application=application,
            status=status,
            created_by=request.user,
            notes=f'Bulk {action} action'
        )

    messages.success(request, f'Successfully processed selected applications.')
    return redirect('applications:application_list')

class AnalyticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'applications/analytics.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Time-based analytics
        context['monthly_applications'] = Application.objects.annotate(
            month=TruncMonth('submitted_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Program success rates
        context['program_success_rates'] = Program.objects.annotate(
            total_apps=Count('application'),
            approved_apps=Count('application', filter=Q(application__status='approved')),
            success_rate=ExpressionWrapper(
                F('approved_apps') * 100.0 / F('total_apps'),
                output_field=FloatField()
            )
        ).filter(total_apps__gt=0)
        
        # Processing time analytics
        context['avg_processing_time'] = Application.objects.exclude(
            reviewed_by__isnull=True
        ).annotate(
            processing_time=ExpressionWrapper(
                F('updated_at') - F('submitted_at'),
                output_field=DurationField()
            )
        ).aggregate(avg_time=Avg('processing_time'))
        
        return context

@login_required
def notification_preferences(request):
    preference, created = NotificationPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        preference.email_on_status_change = request.POST.get('email_on_status_change') == 'on'
        preference.email_on_review = request.POST.get('email_on_review') == 'on'
        preference.email_on_document_request = request.POST.get('email_on_document_request') == 'on'
        preference.save()
        messages.success(request, 'Notification preferences updated successfully.')
        
    return render(request, 'applications/notification_preferences.html', {
        'preference': preference
    })

# Analytics View
