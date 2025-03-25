from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Lead, LeadNote, LeadDocument
from .forms import LeadNoteForm, LeadDocumentForm
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.

class LeadNoteAndDocumentTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            password='12345'
        )
        
        # Create a test lead
        self.lead = Lead.objects.create(
            company_name='Test Company',
            contact_person='John Doe',
            email='john@example.com',
            created_by=self.user
        )
        
        # Log in the test user
        self.client.login(username='testuser', password='12345')

    def test_lead_note_form_valid(self):
        """Test that LeadNoteForm is valid with correct data"""
        form_data = {
            'content': 'This is a test note for the lead'
        }
        form = LeadNoteForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_lead_document_form_valid(self):
        """Test that LeadDocumentForm is valid with correct data"""
        # Create a test file
        test_file = SimpleUploadedFile(
            name='test_document.pdf', 
            content=b'This is a test PDF content', 
            content_type='application/pdf'
        )
        
        form_data = {
            'description': 'Test document description'
        }
        form_files = {
            'file': test_file
        }
        
        form = LeadDocumentForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_add_note_to_lead(self):
        """Test adding a note to a lead via POST request"""
        url = reverse('leads:lead_detail', kwargs={'pk': self.lead.pk})
        
        # Prepare note data
        note_data = {
            'action': 'add_note',
            'content': 'This is a test note added via POST'
        }
        
        # Send POST request to add note
        response = self.client.post(url, data=note_data)
        
        # Check redirect and note creation
        self.assertEqual(response.status_code, 302)  # Redirect after successful note addition
        self.assertTrue(LeadNote.objects.filter(
            lead=self.lead, 
            content='This is a test note added via POST'
        ).exists())

    def test_add_document_to_lead(self):
        """Test uploading a document to a lead via POST request"""
        url = reverse('leads:lead_detail', kwargs={'pk': self.lead.pk})
        
        # Create a test file
        test_file = SimpleUploadedFile(
            name='test_document.pdf', 
            content=b'This is a test PDF content', 
            content_type='application/pdf'
        )
        
        # Prepare document data
        document_data = {
            'action': 'add_document',
            'file': test_file,
            'description': 'Test document upload'
        }
        
        # Send POST request to add document
        response = self.client.post(url, data=document_data)
        
        # Check redirect and document creation
        self.assertEqual(response.status_code, 302)  # Redirect after successful document upload
        self.assertTrue(LeadDocument.objects.filter(
            lead=self.lead, 
            description='Test document upload'
        ).exists())

    def test_lead_detail_view_context(self):
        """Test that lead detail view provides correct context for notes and documents"""
        # Create a test note
        LeadNote.objects.create(
            lead=self.lead, 
            content='Test Note Context',
            created_by=self.user
        )
        
        # Create a test document
        test_file = SimpleUploadedFile(
            name='test_context_document.pdf', 
            content=b'Context test document', 
            content_type='application/pdf'
        )
        LeadDocument.objects.create(
            lead=self.lead, 
            file=test_file,
            description='Test Document Context',
            created_by=self.user
        )
        
        # Get lead detail view
        url = reverse('leads:lead_detail', kwargs={'pk': self.lead.pk})
        response = self.client.get(url)
        
        # Check context
        self.assertIn('notes', response.context)
        self.assertIn('documents', response.context)
        
        # Check note in context
        notes = response.context['notes']
        self.assertTrue(any(note.content == 'Test Note Context' for note in notes))
        
        # Check document in context
        documents = response.context['documents']
        self.assertTrue(any(doc.description == 'Test Document Context' for doc in documents))

    def test_note_list_view(self):
        """Test the note list view for a specific lead"""
        # Create multiple notes
        LeadNote.objects.create(
            lead=self.lead, 
            content='First Test Note',
            created_by=self.user
        )
        LeadNote.objects.create(
            lead=self.lead, 
            content='Second Test Note',
            created_by=self.user
        )
        
        # Get note list view
        url = reverse('leads:lead_note_list', kwargs={'lead_pk': self.lead.pk})
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'leads/lead_note_list.html')
        
        # Check context
        self.assertIn('notes', response.context)
        notes = response.context['notes']
        self.assertEqual(notes.count(), 2)
        self.assertTrue(any(note.content == 'First Test Note' for note in notes))
        self.assertTrue(any(note.content == 'Second Test Note' for note in notes))

    def test_document_list_view(self):
        """Test the document list view for a specific lead"""
        # Create multiple documents
        test_file1 = SimpleUploadedFile(
            name='test_doc1.pdf', 
            content=b'First test document', 
            content_type='application/pdf'
        )
        test_file2 = SimpleUploadedFile(
            name='test_doc2.pdf', 
            content=b'Second test document', 
            content_type='application/pdf'
        )
        
        LeadDocument.objects.create(
            lead=self.lead, 
            file=test_file1,
            description='First Test Document',
            created_by=self.user
        )
        LeadDocument.objects.create(
            lead=self.lead, 
            file=test_file2,
            description='Second Test Document',
            created_by=self.user
        )
        
        # Get document list view
        url = reverse('leads:lead_document_list', kwargs={'lead_pk': self.lead.pk})
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'leads/lead_document_list.html')
        
        # Check context
        self.assertIn('documents', response.context)
        documents = response.context['documents']
        self.assertEqual(documents.count(), 2)
        self.assertTrue(any(doc.description == 'First Test Document' for doc in documents))
        self.assertTrue(any(doc.description == 'Second Test Document' for doc in documents))
