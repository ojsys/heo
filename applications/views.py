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
from django.urls import reverse
from django.forms import modelformset_factory
import json
from django.db.models.functions import TruncMonth
from django.db.models import Count, Avg, Q, F, FloatField, DurationField, ExpressionWrapper
from .models import Program, Application, ApplicationDocument, NotificationPreference, ApplicationStatus, FormField
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


# Add this helper function to handle date serialization
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = Application
    template_name = 'applications/application_form.html'
    form_class = ApplicationForm
    login_url = '/login/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.program = get_object_or_404(Program, pk=self.kwargs['program_id'])
        kwargs['program'] = self.program
        kwargs['user'] = self.request.user  # Pass the user to the form
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['program'] = self.program
        
        # Add form fields specific to this program
        context['form_fields'] = FormField.objects.filter(program=self.program).order_by('order')
        
        # Add document formset
        DocumentFormSet = modelformset_factory(
            ApplicationDocument,
            form=ApplicationDocumentForm,
            extra=1,
            can_delete=True
        )
        
        if self.request.POST:
            context['document_formset'] = DocumentFormSet(
                self.request.POST, 
                self.request.FILES,
                queryset=ApplicationDocument.objects.none()
            )
        else:
            context['document_formset'] = DocumentFormSet(queryset=ApplicationDocument.objects.none())
            
        return context

    def form_valid(self, form):
        # Get the document formset from context
        context = self.get_context_data()
        document_formset = context['document_formset']
        
        # Check if document formset is valid before proceeding
        if not document_formset.is_valid():
            # Add formset errors to the form
            for error in document_formset.errors:
                for field, message in error.items():
                    form.add_error(None, f"Document error: {message}")
            return self.form_invalid(form)
        
        # Process form data from dynamic fields
        form_data = {}
        
        # Add the personal information fields to form_data
        personal_info = {
            'first_name': form.cleaned_data.get('first_name'),
            'last_name': form.cleaned_data.get('last_name'),
            'email': form.cleaned_data.get('email'),
            'phone_number': form.cleaned_data.get('phone_number'),
            'address': form.cleaned_data.get('address'),
            'city': form.cleaned_data.get('city'),
            'state': form.cleaned_data.get('state'),
            'zip_code': form.cleaned_data.get('zip_code'),
            'country': form.cleaned_data.get('country'),
        }
        
        # Handle date_of_birth separately to avoid JSON serialization issues
        date_of_birth = form.cleaned_data.get('date_of_birth')
        if date_of_birth:
            personal_info['date_of_birth'] = date_of_birth.isoformat()
        
        form_data.update(personal_info)
        
        # Add program-specific fields
        for field in FormField.objects.filter(program=self.program):
            field_name = f'field_{field.id}'
            if field_name in self.request.POST:
                value = self.request.POST.get(field_name)
                # Handle potential date fields in program-specific fields
                if field.field_type == 'date' and value:
                    try:
                        # Try to parse the date and convert to ISO format
                        parsed_date = datetime.strptime(value, '%Y-%m-%d').date()
                        value = parsed_date.isoformat()
                    except ValueError:
                        # If parsing fails, keep the original value
                        pass
                form_data[field_name] = value
        
        # Set application properties
        form.instance.form_data = json.dumps(form_data, default=json_serial)
        form.instance.applicant = self.request.user
        form.instance.program = self.program
        form.instance.status = 'submitted'
        form.instance.submitted_at = timezone.now()
        
        # Save the application
        try:
            self.object = form.save()
            
            # Save documents
            documents = document_formset.save(commit=False)
            for document in documents:
                document.application = self.object
                document.save()
            
            # Handle deleted documents
            for obj in document_formset.deleted_objects:
                obj.delete()
            
            # Create initial application status
            ApplicationStatus.objects.create(
                application=self.object,
                status='submitted',
                created_by=self.request.user,
                notes='Application submitted'
            )
            
            messages.success(self.request, f'Your application for {self.program.name} has been submitted successfully!')
            return redirect(self.get_success_url())
        except Exception as e:
            # Log the error for debugging
            print(f"Error saving application: {str(e)}")
            form.add_error(None, f"An error occurred while saving your application: {str(e)}")
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'There was an error with your application. Please check the form and try again.')
        # Print form errors for debugging
        print(f"Form errors: {form.errors}")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('applications:application_detail', kwargs={'pk': self.object.pk})

@login_required
def my_applications(request):
    """View for users to see all their applications"""
    applications = Application.objects.filter(
        applicant=request.user
    ).select_related('program').order_by('-submitted_at')
    
    return render(request, 'applications/my_applications.html', {
        'applications': applications
    })

@login_required
def program_apply(request, program_id):
    """Redirect to application form or existing application"""
    program = get_object_or_404(Program, pk=program_id, is_active=True)
    
    # Check if application deadline has passed (if the field exists)
    if hasattr(program, 'application_deadline') and program.application_deadline and program.application_deadline < timezone.now().date():
        messages.error(request, f"The application deadline for {program.name} has passed.")
        return redirect('applications:program_detail', pk=program_id)
    
    # Check if user already has an application for this program
    existing_application = Application.objects.filter(
        applicant=request.user,
        program=program
    ).first()
    
    if existing_application:
        messages.info(request, f"You already have an application for {program.name}.")
        return redirect('applications:application_detail', pk=existing_application.pk)
    
    return redirect('applications:application_create', program_id=program_id)
        

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
    application = get_object_or_404(Application, pk=pk)
    
    # Check if user is authorized to review this application
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "You are not authorized to review applications.")
        return redirect('applications:dashboard')
    
    if request.method == 'POST':
        form = ApplicationReviewForm(request.POST, instance=application)
        if form.is_valid():
            # Save only the review_notes field to the application
            application = form.save(commit=False)
            
            # Update application status if needed
            if form.cleaned_data.get('update_status'):
                new_status = form.cleaned_data.get('status')
                
                # Only update if there's a change in status
                if application.status != new_status:
                    application.status = new_status
                    
                    # Create a status update record
                    ApplicationStatus.objects.create(
                        application=application,
                        status=application.status,
                        created_by=request.user,
                        notes=form.cleaned_data.get('notes', '')
                    )
            
            # Save the application with the updated review_notes
            application.save()
            
            # Send notification
            send_application_status_update(application)
            
            messages.success(request, "Review saved successfully.")
            return redirect('applications:application_detail', pk=application.pk)
    else:
        form = ApplicationReviewForm(instance=application)
    
    # Parse the JSON form data for display
    try:
        form_data = json.loads(application.form_data) if application.form_data else {}
    except:
        form_data = {}
    
    return render(request, 'applications/application_review.html', {
        'application': application,
        'form': form,
        'form_data': form_data
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


@login_required
def user_dashboard(request):
    """Dashboard for users to track their applications and get updates"""
    # Get all applications for the current user
    applications = Application.objects.filter(
        applicant=request.user
    ).select_related('program').order_by('-submitted_at')
    
    # Count applications by status
    pending_count = applications.filter(status__in=['submitted', 'under_review']).count()
    approved_count = applications.filter(status='approved').count()
    
    # Get recent status updates
    recent_status_updates = ApplicationStatus.objects.filter(
        application__applicant=request.user
    ).select_related('application', 'application__program').order_by('-created_at')[:5]
    
    # Get notification preferences
    notification_prefs, created = NotificationPreference.objects.get_or_create(user=request.user)
    
    return render(request, 'applications/user_dashboard.html', {
        'applications': applications,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'recent_status_updates': recent_status_updates,
        'notification_prefs': notification_prefs,
    })
