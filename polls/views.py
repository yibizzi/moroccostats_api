from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader

from .models import Question
# Create your views here.

def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    template = loader.get_template('polls/index.html')
    context = {
        'latest_question_list': latest_question_list,
    }
    return HttpResponse(template.render(context, request))

def detail(request, question_id):
    try:
        q = Question.objects.get(id=question_id)
        choices = q.choice_set.all()
        qst_text = q.question_text
        context = {
            'question':q,
            'choices':choices,
            'qst':qst_text,
        }
        return HttpResponse(render(request, 'polls/question_detail.html', context))
    except Question.DoesNotExist:
        raise Http404("Question does not exist")

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)


