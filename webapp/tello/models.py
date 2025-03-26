from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    teacherid = models.AutoField(primary_key=True)
    teachername = models.CharField(max_length=100)
    teachergrade = models.CharField(max_length=50)

    def __str__(self):
        return self.teachername


class Student(models.Model):
    studentid = models.AutoField(primary_key=True)
    studentcode = models.CharField(max_length=4, unique=True)
    studentname = models.CharField(max_length=100)
    studentgrade = models.CharField(max_length=50)
    studentage = models.IntegerField()
    assignedteacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    additional_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.studentname


class VocabularyCategory(models.Model):
    """
    Represents categories like Nouns, Verbs, Adjectives, etc.
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class VocabularyWord(models.Model):
    """
    Represents individual words belonging to a category.
    """
    word = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(
        VocabularyCategory, on_delete=models.CASCADE, related_name="words")

    def __str__(self):
        return self.word


class StudentVocabulary(models.Model):
    """
    Stores vocabulary words learned by each student.
    """
    student = models.ForeignKey(
        "Student", on_delete=models.CASCADE, related_name="vocabulary")
    word = models.ForeignKey(
        VocabularyWord, on_delete=models.CASCADE, related_name="learned_by")

    class Meta:
        # Prevent duplicate words for a student
        unique_together = ('student', 'word')

    def __str__(self):
        return f"{self.student.studentname} - {self.word.word}"


class StorySession(models.Model):
    """
    Represents a session where a student engages with a particular story.
    Tracks session timing and duration.
    """
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="sessions")
    story_id = models.IntegerField()  # Not a ForeignKey, as requested
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)  # Auto-calculated
    date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            self.duration = self.end_time - self.start_time
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Session for {self.student.studentname} - Story {self.story_id}"


class StudentReport(models.Model):
    """
    Stores evaluation metrics for a storytelling session.
    Now linked to StorySession instead of student and story_id separately.
    """
    story_session = models.ForeignKey(
        StorySession, on_delete=models.CASCADE, related_name="reports")
    vocab_score = models.FloatField()
    structure_sim_score = models.FloatField()
    response_length = models.FloatField()
    avg_engagement = models.FloatField()
    final_score = models.FloatField()
    prompt_interaction_ratio = models.FloatField()
    prompt_interaction_count = models.IntegerField()
    feedback_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.story_session.student.studentname} - Story {self.story_session.story_id}"
