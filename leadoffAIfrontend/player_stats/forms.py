from django import forms

class PlayerSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search for a player...',
            'class': 'search-input',
            'aria-label': 'Search for a player'
        })
    )