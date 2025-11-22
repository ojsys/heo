from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from django.utils.safestring import mark_safe
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
    readonly_fields = ('submitted_at', 'document_preview')

    fieldsets = (
        (None, {
            'fields': ('user', 'status', 'rejection_reason')
        }),
        ('Documents', {
            'fields': ('id_document', 'address_proof', 'document_preview')
        }),
        ('Verification Info', {
            'fields': ('submitted_at', 'verified_at', 'verified_by')
        }),
    )

    class Media:
        css = {
            'all': ('admin/css/verification_modal.css',)
        }
        js = ('admin/js/verification_modal.js',)

    def view_documents(self, obj):
        """Display clickable image thumbnails in the list view."""
        html_parts = []

        if obj.id_document:
            html_parts.append(format_html(
                '<a href="#" class="view-doc-btn" data-url="{}" data-title="ID Document">'
                '<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:4px;margin-right:5px;" '
                'title="Click to view ID Document" />'
                '</a>',
                obj.id_document.url,
                obj.id_document.url
            ))

        if obj.address_proof:
            html_parts.append(format_html(
                '<a href="#" class="view-doc-btn" data-url="{}" data-title="Address Proof">'
                '<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:4px;" '
                'title="Click to view Address Proof" />'
                '</a>',
                obj.address_proof.url,
                obj.address_proof.url
            ))

        if not html_parts:
            return "No documents"

        return mark_safe(''.join(html_parts))

    view_documents.short_description = 'Documents'

    def document_preview(self, obj):
        """Display larger document previews in the detail view with modal support."""
        html = '''
        <style>
            .doc-preview-container { display: flex; gap: 20px; flex-wrap: wrap; }
            .doc-preview-item { text-align: center; }
            .doc-preview-item img {
                max-width: 200px;
                max-height: 200px;
                object-fit: contain;
                border: 1px solid #ddd;
                border-radius: 8px;
                cursor: pointer;
                transition: transform 0.2s;
            }
            .doc-preview-item img:hover { transform: scale(1.05); }
            .doc-preview-label {
                display: block;
                margin-top: 8px;
                font-weight: bold;
                color: #333;
            }

            /* Modal Styles */
            .verification-modal {
                display: none;
                position: fixed;
                z-index: 10000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.9);
            }
            .verification-modal-content {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                max-width: 90%;
                max-height: 90%;
            }
            .verification-modal-content img {
                max-width: 100%;
                max-height: 85vh;
                object-fit: contain;
            }
            .verification-modal-close {
                position: absolute;
                top: 15px;
                right: 35px;
                color: #f1f1f1;
                font-size: 40px;
                font-weight: bold;
                cursor: pointer;
            }
            .verification-modal-close:hover { color: #bbb; }
            .verification-modal-title {
                color: #fff;
                text-align: center;
                padding: 10px;
                font-size: 18px;
            }
        </style>

        <!-- Modal -->
        <div id="verificationModal" class="verification-modal">
            <span class="verification-modal-close" onclick="closeVerificationModal()">&times;</span>
            <div class="verification-modal-content">
                <div class="verification-modal-title" id="modalTitle"></div>
                <img id="modalImage" src="" alt="Document Preview">
            </div>
        </div>

        <div class="doc-preview-container">
        '''

        if obj.id_document:
            html += format_html(
                '''
                <div class="doc-preview-item">
                    <img src="{}" alt="ID Document" onclick="openVerificationModal('{}', 'ID Document')" />
                    <span class="doc-preview-label">ID Document</span>
                </div>
                ''',
                obj.id_document.url,
                obj.id_document.url
            )

        if obj.address_proof:
            html += format_html(
                '''
                <div class="doc-preview-item">
                    <img src="{}" alt="Address Proof" onclick="openVerificationModal('{}', 'Address Proof')" />
                    <span class="doc-preview-label">Address Proof</span>
                </div>
                ''',
                obj.address_proof.url,
                obj.address_proof.url
            )

        html += '''
        </div>

        <script>
            function openVerificationModal(url, title) {
                document.getElementById('modalImage').src = url;
                document.getElementById('modalTitle').textContent = title;
                document.getElementById('verificationModal').style.display = 'block';
            }

            function closeVerificationModal() {
                document.getElementById('verificationModal').style.display = 'none';
            }

            // Close modal when clicking outside the image
            document.getElementById('verificationModal').onclick = function(e) {
                if (e.target === this) {
                    closeVerificationModal();
                }
            }

            // Close modal with Escape key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    closeVerificationModal();
                }
            });
        </script>
        '''

        if not obj.id_document and not obj.address_proof:
            return "No documents uploaded"

        return mark_safe(html)

    document_preview.short_description = 'Document Preview'

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