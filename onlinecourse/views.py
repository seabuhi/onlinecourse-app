from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Course, Enrollment, Question, Choice, Submission
import logging

logger = logging.getLogger(__name__)


def submit(request, course_id):
    user = request.user
    course = get_object_or_404(Course, pk=course_id)
    try:
        enrollment = Enrollment.objects.get(user=user, course=course)
    except Enrollment.DoesNotExist:
        return HttpResponseRedirect(reverse('onlinecourse:enroll', args=(course.id,)))

    submission = Submission(enrollment=enrollment)
    submission.save()

    for key, values in request.POST.items():
        if key.startswith('choice'):
            for value in request.POST.getlist(key):
                choice = Choice.objects.get(pk=value)
                submission.choices.add(choice)
    submission.save()

    return HttpResponseRedirect(
        reverse('onlinecourse:show_exam_result', args=(course.id, submission.id))
    )


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    selected_ids = submission.choices.values_list('id', flat=True)

    total_score = 0
    for question in course.lesson_set.all().values_list(
        'question', flat=True
    ):
        q = Question.objects.get(pk=question)
        if q.is_get_score(selected_ids):
            total_score += q.grade

    context = {
        'course': course,
        'submission': submission,
        'selected_ids': selected_ids,
        'total_score': total_score,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)