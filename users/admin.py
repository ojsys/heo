from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import User, UserVerification

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'user_type', 'is_verified', 'date_joined')
    list_filter = ('user_type', 'is_verified', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
            'fields': ('username', 'first_name', 'last_name', 'phone_number', 
                      'address', 'date_of_birth', 'profile_picture')
        }),
        ('Status', {
            'fields': ('user_type', 'is_verified', 'is_active')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'user_type'),
        }),
    )

@admin.register(UserVerification)
class UserVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'submitted_at', 'verified_at', 'view_documents')
    list_filter = ('status', 'submitted_at', 'verified_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('submitted_at',)
    
    def view_documents(self, obj):
        links = []
        if obj.id_document:
            links.append(format_html('<a href="{}" target="_blank">ID Document</a>', obj.id_document.url))
        if obj.address_proof:
            links.append(format_html('<a href="{}" target="_blank">Address Proof</a>', obj.address_proof.url))
        return format_html(' | '.join(links))
    view_documents.short_description = 'Documents'

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            if obj.status == 'approved':
                obj.verified_at = timezone.now()
                obj.verified_by = request.user
                obj.user.is_verified = True
                obj.user.save()
            elif obj.status == 'rejected':
                obj.verified_at = timezone.now()
                obj.verified_by = request.user
        super().save_model(request, obj, form, change)