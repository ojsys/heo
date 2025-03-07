from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Page, Media, ImpactStory, Announcement

class PageListView(ListView):
    model = Page
    template_name = 'cms/page_list.html'
    context_object_name = 'pages'
    queryset = Page.objects.filter(is_published=True)

class PageDetailView(DetailView):
    model = Page
    template_name = 'cms/page_detail.html'
    context_object_name = 'page'

class PageCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Page
    template_name = 'cms/page_form.html'
    fields = ['title', 'content', 'meta_description', 'featured_image', 'is_published']
    success_url = reverse_lazy('cms:page_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_staff

class ImpactStoryListView(ListView):
    model = ImpactStory
    template_name = 'cms/impact_story_list.html'
    context_object_name = 'stories'
    queryset = ImpactStory.objects.filter(is_featured=True)

class AnnouncementListView(ListView):
    model = Announcement
    template_name = 'cms/announcement_list.html'
    context_object_name = 'announcements'
    queryset = Announcement.objects.filter(is_published=True)