from django.db import models
from django.contrib.auth.models import User


class Analysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume_text = models.TextField()
    job_description = models.TextField()

    match_score = models.IntegerField(default=0)

    matched_skills = models.TextField(blank=True)
    missing_skills = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.match_score}%"