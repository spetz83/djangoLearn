import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question


def createQuestion(questionText, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=questionText, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])


    def test_past_question(self):
        createQuestion(questionText="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], ['<Question: Past question.>']
        )


    def test_future_question(self):
        createQuestion(questionText='Future question.', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])


    def test_future_question_and_past_question(self):
        createQuestion(questionText="Past question.", days=-30)
        createQuestion(questionText="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], ['<Question: Past question.>']
        )


    def test_two_past_questions(self):
        createQuestion(questionText="Past question 1.", days=-30)
        createQuestion(questionText="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        futureQuestion = createQuestion(questionText="Future question.", days=5)
        url = reverse('polls:detail', args=(futureQuestion.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


    def test_past_question(self):
        pastQuestion = createQuestion(questionText="Past question.", days=-5)
        url = reverse('polls:detail', args=(pastQuestion.id,))
        response = self.client.get(url)
        self.assertContains(response, pastQuestion.question_text)


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        futureQuestion = Question(pub_date=time)
        self.assertIs(futureQuestion.wasPublishedRecently(), False)


    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        oldQuestion = Question(pub_date=time)
        self.assertIs(oldQuestion.wasPublishedRecently(), False)


    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recentQuestion = Question(pub_date=time)
        self.assertIs(recentQuestion.wasPublishedRecently(), True)

