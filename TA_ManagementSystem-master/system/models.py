from django.db import models
from django.contrib.auth.models import User


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name + self.user.last_name


class TA(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # %Y: year, %M: month, %D: day
    cv = models.FileField(blank=True, null=True, upload_to="cvs/%Y/%m/%d/")
    # expectedCourseNumber = models.IntegerField(default=0)

    # department = models.CharField()

    def __str__(self):
        return self.user.first_name + self.user.last_name


class DepartmentHead(models.Model):
    department = models.CharField(max_length=20, default="")
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name + self.user.last_name


class Course(models.Model):
    instructor = models.ForeignKey(Teacher, on_delete=models.CASCADE)  # instructor_id
    CRN = models.CharField(max_length=5)
    semester = models.CharField(max_length=10)
    title = models.CharField(max_length=50)
    subject = models.CharField(max_length=4)
    courseName = models.CharField(max_length=30)
    capacity = models.IntegerField(default=0)

    def __str__(self):
        return self.subject + self.courseName


class TADuty(models.Model):
    curriculum = models.ForeignKey(Course, on_delete=models.CASCADE)  # curriculum_id
    labNumber = models.IntegerField(default=0)
    preparationHour = models.FloatField(default=0)
    labHour = models.FloatField(default=0)
    labWorkingHour = models.FloatField(default=0)
    assignmentNumber = models.IntegerField(default=0)
    assignmentWorkingHour = models.FloatField(default=0)
    contactHour = models.FloatField(default=0)
    otherDutiesHour = models.FloatField(default=0)
    totalHour = models.FloatField(default=0)
    recommendedTANumber = models.IntegerField(default=0)

    def __str__(self):
        return self.curriculum.subject + self.curriculum.courseName


# course rank applicant
class RankTA(models.Model):
    curriculum = models.ForeignKey(Course, on_delete=models.CASCADE)
    TA = models.ForeignKey(TA, on_delete=models.CASCADE)
    ranking = models.IntegerField(default=0)  # ranking for TA

    def __str__(self):
        return self.curriculum.subject + self.curriculum.courseName


# applicant rank course
class RankCourse(models.Model):
    rowid = models.CharField(max_length=50)
    id = models.CharField(primary_key=True,max_length=50)
    TA_id = models.CharField(max_length=50)
    curriculum_id = models.CharField(max_length=50)
    ranking = models.CharField(max_length=50)  # ranking for course



class MatchResult(models.Model):
    curriculum = models.ForeignKey(Course, on_delete=models.CASCADE)  # course
    TA = models.ForeignKey(TA, on_delete=models.CASCADE)  # TA
    courseRanking = models.IntegerField(default=0)  # rank
    TARanking = models.IntegerField(default=0)
    positions = models.IntegerField(default=0)
    status = models.BooleanField(default=False)






