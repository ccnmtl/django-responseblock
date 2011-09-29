from django.db import models
from pagetree.models import PageBlock, Hierarchy, Section
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django import forms
from datetime import datetime
from django.core.urlresolvers import reverse
from quizblock.models import Quiz,Question

def all_questions():
    # TODO: this will break in sites with more than one hierarchy
    h = Hierarchy.objects.all()[0]
    quizzes = []
    for s in h.get_root().get_descendants():
        for p in s.pageblock_set.all():
            if hasattr(p.block(),'needs_submit') and p.block().needs_submit():
                quizzes.append(p)

    questions = []
    for qz in quizzes:
        for q in qz.block().question_set.all():
            if hasattr(q,'quiz'):
                yield q

class Response(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    question = models.ForeignKey(Question,related_name="question")
    template_file = "responseblock/responseblock.html"

    display_name = "Response"
    exportable = False
    importable = False

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def edit_form(self):
        question_choices = [
            (q.id,"%s%s/%s" % (q.quiz.pageblock().section.get_absolute_url(),
                               q.quiz.pageblock().label,
                               q.text)) for q in all_questions()
            ]

        class EditForm(forms.Form):
            question = forms.ChoiceField(label="Select Question",
                                         choices=question_choices)
        return EditForm(instance=self)

    @classmethod
    def add_form(self):
        question_choices = [
            (q.id,"%s%s/%s" % (q.quiz.pageblock().section.get_absolute_url(),
                               q.quiz.pageblock().label,
                               q.text)) for q in all_questions()
            ]
        class AddForm(forms.Form):
            question = forms.ChoiceField(label="Select Question",
                                         choices=question_choices,
                                         )
        return AddForm()

    @classmethod
    def create(self,request):
        question = Question.objects.get(id=request.POST.get('question',''))
        return Response.objects.create(question=question)

    def edit(self,vals,files):
        question = Question.objects.get(id=vals.get('question',''))
        self.question = question
        self.save()
