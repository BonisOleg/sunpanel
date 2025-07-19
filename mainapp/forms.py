from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['client_name', 'client_position', 'review_text', 'rating', 'project_type', 'location']
        widgets = {
            'client_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': "Ваше ім'я",
                'required': True
            }),
            'client_position': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Посада або назва компанії (необовязково)'
            }),
            'review_text': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Поділіться вашим досвідом співпраці з нами...',
                'rows': 4,
                'required': True
            }),
            'rating': forms.Select(attrs={
                'class': 'form-select'
            }),
            'project_type': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Тип проєкту (необовязково)'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Місто або область (необовязково)'
            })
        }
        labels = {
            'client_name': "Ваше ім'я",
            'client_position': 'Посада/Компанія',
            'review_text': 'Ваш відгук',
            'rating': 'Оцінка',
            'project_type': 'Тип проєкту',
            'location': 'Локація'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].choices = [
            ('', 'Оберіть оцінку'),
            (5, '5 зірок - Відмінно'),
            (4, '4 зірки - Добре'),
            (3, '3 зірки - Задовільно'),
            (2, '2 зірки - Погано'),
            (1, '1 зірка - Дуже погано'),
        ] 