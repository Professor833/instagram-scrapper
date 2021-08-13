from django import forms


class CalculateInstagramEngagement(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': "w-full bg-gray-100 bg-opacity-50 rounded border border-gray-300 focus:border-indigo-500 focus:bg-transparent focus:ring-2 focus:ring-indigo-200 text-base outline-none text-gray-700 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out"}))
