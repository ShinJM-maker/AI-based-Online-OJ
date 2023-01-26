from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models import Problem

class ProblemListView(ListView):
    model = Problem

class ProblemDetailView(DetailView):
    model = Problem

