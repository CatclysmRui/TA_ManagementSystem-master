from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt

from .models import Teacher, TA, DepartmentHead, TADuty, Course, RankTA, RankCourse, MatchResult
from .forms import DutyCreateForm
from django.shortcuts import redirect
from django.db.models import Q, Max, Count
import json
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from math import ceil
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
import xlwt
import heapq


def loginpage(request):
    rankingFunction()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            request.session['username'] = username
            return render(request, "semester.html")
        else:
            return render(request, 'registration/login.html')
    return render(request, 'registration/login.html')


def select_semester(request):

    if request.method == "POST":
        semester = request.POST['semester']
        if semester is not None:
            request.session['semester'] = semester
            username = request.session['username']
            user = User.objects.get(username=username)
            role = []
            courseList = Course.objects.filter(semester=request.session['semester'])
            userList = User.objects.get(username=request.session['username'])
            gender = userList.email.split("#", 1)



            if courseList.exists():
                courseList = courseList
            else:
                courseList = 'No course in this semester'

            if Teacher.objects.filter(user__username=username).exists():
                role.append("instructor")
                request.session['role'] = role
                #send professors course to page
                professorID = Teacher.objects.get(user_id=user.id)

                try:
                    teacherCourse = Course.objects.filter(instructor_id=professorID.id,semester=request.session['semester'])

                except Course.DoesNotExist:
                    pass
                #send end
                #send TA list to page
                allTAList = TA.objects.filter()
                allUserList = User.objects.filter()
                #send end
                #send selected TA list to page
                selectedTA = RankTA.objects.filter()
                #send end
                #match result
                matchingResult = MatchResult.objects.filter()
                return render(request, 'professorMain.html', {'user': user, 'courseList': courseList, 'userList':userList, 'teacherCourse': teacherCourse, 'allTAList':allTAList, 'allUserList':allUserList, 'selectedTA':selectedTA,'matchingResult':matchingResult})
            if TA.objects.filter(user__username=username).exists():
                role.append("TA")
                request.session['role'] = role
                #send ranked course to page

                TAId = TA.objects.get(user_id=user.id)

                try:
                    selectCourseId = RankCourse.objects.filter(TA_id=TAId.id)

                except RankCourse.DoesNotExist:
                    pass


                #send end
                #get ranking result
                matchingResult = MatchResult.objects.filter(TA_id=TAId.id)
                print(matchingResult)
                return render(request, 'taMain.html', {'user': user, 'courseList': courseList, 'userList':userList, 'email':gender[0], 'gender':gender[1], 'selectCourseId':selectCourseId,'matchingResult':matchingResult})
            if DepartmentHead.objects.filter(user__username=username).exists():
                role.append("departmenthead")
                request.session['role'] = role
                allTAList = TA.objects.filter()
                matchingResult = MatchResult.objects.filter()
                return render(request, 'deptheadMain.html', {'user': user, 'courseList': courseList, 'userList':userList, 'allTAList':allTAList,'matchingResult':matchingResult})

            return render(request, 'home.html', {'user': user})

    return HttpResponse('please select semester')

#course search function in TA main page
@csrf_exempt
def courseSearch(request):
    if request.POST:
        searchData = request.POST['keyword']

        searchResult = Course.objects.filter(title__icontains=searchData)

        if searchResult.exists():
            print(searchResult)
            searchResult2 = []
            for s in searchResult:
                searchResult2.append({"courseName": s.courseName, "title": s.title})

            return HttpResponse(json.dumps(searchResult2), content_type="application/json")

        else:

            return HttpResponse("-1")

#TA search function in professor main page
@csrf_exempt
def taSearch(request):
    if request.POST:
        searchData = request.POST['keyword']
        allTAList = TA.objects.filter()
        searchResult2 = []
        flag =0
        for s in allTAList:


            if searchData in s.user.username:
                 searchResult2.append({"taName": s.user.first_name, "id": s.user.id})
                 flag = flag + 1



        if flag >0:
            return HttpResponse(json.dumps(searchResult2), content_type="application/json")
        else:
            return HttpResponse("-1")

def logout(request):
    try:
        del request.session['username']
    except KeyError:
        pass
    return render(request, 'registration/logout.html')


# course list for each instructor
# id: user id
def course_list(request, id):
    teacher = Teacher.objects.get(user_id=id)
    semester = request.session['semester']
    courses = teacher.course_set.filter(semester=semester)
    if courses.exists():
        return render(request, 'course.html', {'courses': courses})
    else:
        return HttpResponse('no course this semester')


# course corresponds TA duty
# id: course id
def duty_detail(request, id):
    course = Course.objects.get(id=id)
    taDuty = TADuty.objects.get(curriculum_id=id)
    return render(request, 'duty_detail.html', {'taDuty': taDuty, 'course': course})


# ta duty for each course
# id: course id
def ta_duty(request, id):
    taDuty = TADuty.objects.get(curriculum_id=id)
    if request.method == 'GET':
        context = {
            'labNumber': taDuty.labNumber,
            'preparationHour': taDuty.preparationHour,
            'labHour': taDuty.labHour,
            'labWorkingHour': taDuty.labWorkingHour,
            'assignmentNumber': taDuty.assignmentNumber,
            'assignmentWorkingHour': taDuty.assignmentWorkingHour,
            'contactHour': taDuty.contactHour,
            'otherDutiesHour': taDuty.otherDutiesHour,
            'totalHour': taDuty.totalHour,
            'recommendedTANumber': taDuty.recommendedTANumber,
        }
        return JsonResponse(context)


# edit TA duty
# id : course id
def duty_edit(request, id):
    duty = get_object_or_404(TADuty, curriculum_id=id)
    if request.method == "POST":
        form = DutyCreateForm(request.POST, instance=duty)
        if form.is_valid():
            course = Course.objects.get(id=id)
            capacity = course.capacity
            # calculate the new total hours for each duty
            lab_number = form.cleaned_data['labNumber']
            preparation_hour = form.cleaned_data['labHour']
            lab_hour = form.cleaned_data['labHour']
            lab_working_hour = form.cleaned_data['labWorkingHour']
            assignment_number = form.cleaned_data['assignmentNumber']
            assignment_working_hour = form.cleaned_data['assignmentWorkingHour']
            contact_hour = form.cleaned_data['contactHour']
            other_duties_hour = form.cleaned_data['otherDutiesHour']
            # total lab hours
            total_lab = capacity * lab_number * (preparation_hour + lab_working_hour + lab_hour)
            # total assignment hours
            total_assignment = capacity * assignment_number * assignment_working_hour
            # total hours
            total = total_lab + total_assignment + contact_hour + other_duties_hour
            # recommended TA numbers
            recommended_ta_number = ceil(total / 180)

            duty = form.save(commit=False)
            duty.totalHour = total
            duty.recommendedTANumber = recommended_ta_number
            duty.save()
            return redirect('duty_detail', id=id)
    else:
        form = DutyCreateForm(instance=duty)
    return render(request, 'duty_edit.html', {'form': form})


# instructors rank candidate TAs
# id: course id
def ta_list(request, id):
    result = RankTA.objects.filter(curriculum_id=id)
    if result.exists():
        ranking = RankTA.objects.filter(curriculum_id=id).order_by("ranking")
        user = User.objects.get(username=request.session['username'])
        user_id = user.id
        return render(request, "ta_ranking.html", {'user_id': user_id, 'id': id, 'ranking': ranking})

    elif request.is_ajax():
        q = request.GET.get('ta_contains')
        search_qs = TA.objects.filter(Q(user__first_name__icontains=q)
                                      | Q(user__last_name__icontains=q)
                                      ).distinct()
        results = []
        for r in search_qs:
            results.append(r.user.first_name + " " + r.user.last_name)
        data = json.dumps(results)
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)
    else:
        tas = TA.objects.all()
        ta_contains_query = request.GET.get('ta_contains')
        if ta_contains_query != '' and ta_contains_query is not None:
            tas = tas.filter(Q(user__first_name__icontains=ta_contains_query)
                             | Q(user__last_name__icontains=ta_contains_query)
                             ).distinct()
        return render(request, 'ta_list.html', {'tas': tas, 'course_id': id})


# store ranking to db
# id : course id
def rank_ta(request, id):
    if request.method == "POST":
        result = RankTA.objects.filter(curriculum_id=id)
        if result.exists():
            return redirect('ta_list', id=id)
        else:
            rank = request.POST["ranking"]
            ranking_id = rank.split(",")
            ranking_id.pop()  # delete last empty number
            rank_value = 1
            for i in ranking_id:
                ta = TA.objects.get(id=i)
                course = Course.objects.get(id=id)
                RankTA.objects.create(curriculum=course, TA=ta, ranking=rank_value)
                rank_value = rank_value + 1
            ranking = RankTA.objects.filter(curriculum_id=id).order_by("ranking")
            user = User.objects.get(username=request.session['username'])
            user_id = user.id
            return render(request, "ta_ranking.html", {'user_id': user_id, 'id': id, 'ranking': ranking})
    return redirect('ta_list', id=id)


# ======= TA PART =======
# select courses and rank them
def select_course_list(request):
    if request.session.has_key('username'):
        username = request.session['username']
        result = RankCourse.objects.filter(TA__user__username=username)
        if result.exists():
            ta = TA.objects.get(user__username=username)
            ranking = RankCourse.objects.filter(TA_id=ta.id).order_by('ranking')
            return render(request, "course_ranking.html", {'ranking': ranking})

    courses = Course.objects.all()
    return render(request, 'course_list.html', {"courses": courses})


# TA candidates rank referred course
def rank_course(request):
    ta = TA.objects.get(user__username=request.session['username'])
    if ta.cv is None:
        messages.info(request, 'please upload cv first!')  # alert for TA to upload cv first
        return HttpResponseRedirect('/upload/')
    else:
        if request.method == "POST":
            if request.session.has_key('username'):
                username = request.session['username']
                result = RankCourse.objects.filter(TA__user__username=username)
                if result.exists():
                    return redirect('select_course_list')
                else:
                    rank = request.POST["ranking"]
                    ranking_id = rank.split(',')
                    ranking_id.pop()
                    rank_value = 1
                    ta = TA.objects.get(user__username=username)
                    for i in ranking_id:
                        course = Course.objects.get(id=i)
                        RankCourse.objects.create(TA=ta, curriculum=course, ranking=rank_value)
                        rank_value = rank_value + 1
                    ranking = RankCourse.objects.filter(TA_id=ta.id).order_by('ranking')
                    return render(request, "course_ranking.html", {'ranking': ranking})
        return redirect('select_course_list')


# upload cv to server
# name: TA' username
@csrf_exempt
def upload(request):

    if request.method == 'POST':
        file = request.FILES["taCV"]
        if file is not None:
            print("22222")
            ta = TA.objects.get(user__username=request.session["username"])
            ta.cv = file
            ta.save()
            return render(request, 'pageJump.html')
    return render(request, 'upload.html')


# ===============department head==============
# TA and course matching algorithm result
def recommended_allocation(request):
    result = MatchResult.objects.filter(curriculum__semester=request.session['semester'])
    if result.exists():
        return render(request, 'recommended_allocation.html',
                      {'matchingResult': MatchResult.objects.filter(status=True).order_by('curriculum__courseName'),
                       'count': MatchResult.objects.filter(status=True).count()})
    else:
        applicants = TA.objects.all()
        for applicant in applicants:
            matching = MatchResult.objects.filter(TA=applicant).order_by('TARanking')
            for m in matching:
                print(m.curriculum)
                print(MatchResult.objects.filter(curriculum=m.curriculum, status=True).count())
                if MatchResult.objects.filter(curriculum=m.curriculum, status=True).count() < m.positions:
                    print('----')
                    m.status = True
                    m.save()
                    break
                elif MatchResult.objects.filter(curriculum=m.curriculum, status=True).count() is m.positions:
                    for result in MatchResult.objects.filter(curriculum=m.curriculum, status=True).order_by(
                            '-courseRanking'):
                        if m.courseRanking < result.courseRanking:
                            result.status = False
                            break
                        else:
                            continue
        courses = Course.objects.filter(semester=request.session['semester'])
        for course in courses:
            if MatchResult.objects.filter(curriculum=course, status__exact=False).count() is MatchResult.objects.filter(
                    curriculum=course).count():
                position = MatchResult.objects.filter(curriculum=course)[0].positions
                for result in MatchResult.objects.filter(curriculum=course).order_by('courseRanking') and position:
                    result.status = True
                    position = position - 1

        return render(request, 'recommended_allocation.html',
                      {'matchingResult': MatchResult.objects.filter(status=True).order_by('curriculum__courseName'),
                       'count': MatchResult.objects.filter(status=True).count()})


# download TA allocation result file as excel file
def download_excel_data(request):
    if request.method == "POST":
        # content-type of response
        response = HttpResponse(content_type='application/ms-excel')
        # decide file name
        response['Content-Disposition'] = 'attachment; filename="TAAllocationResult.xls"'
        # creating workbook
        wb = xlwt.Workbook(encoding='utf-8')
        # adding sheet
        ws = wb.add_sheet("sheet1")
        # sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        # headers are bold
        font_style.font.bold = True

        style_cell = xlwt.XFStyle()
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = xlwt.Style.colour_map['yellow']  # 设置单元格背景色为黄色
        style_cell.pattern = pattern

        # column header names
        columns = ['term', 'course subject', 'course name', 'instructor', 'TA position(s)', 'student(s)',
                   'student e-mail', 'status']
        # write column header in sheet
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        # sheet body, remaining rows
        font_style = xlwt.XFStyle()

        # get your data, from database or from a text file...
        data = MatchResult.objects.filter(status=True).order_by('curriculum__courseName')
        # get status
        state = request.POST['status']
        rejected_matching = state.split(',')
        rejected_matching.pop()
        for my_row in data:
            row_num = row_num + 1
            ws.write(row_num, 0, my_row.curriculum.semester, font_style)
            ws.write(row_num, 1, my_row.curriculum.subject + my_row.curriculum.courseName, font_style)
            ws.write(row_num, 2, my_row.curriculum.title, font_style)
            ws.write(row_num, 3,
                     my_row.curriculum.instructor.user.first_name + ' ' + my_row.curriculum.instructor.user.last_name,
                     font_style)
            ws.write(row_num, 4, my_row.positions, font_style)
            ws.write(row_num, 5, my_row.TA.user.first_name + ' ' + my_row.TA.user.last_name, font_style)
            ws.write(row_num, 6, my_row.TA.user.email, font_style)
            if str(my_row.id) in rejected_matching:
                ws.write(row_num, 7, 'rejected', style_cell)
            else:
                ws.write(row_num, 7, 'accepted', font_style)
        wb.save(response)
        return response
    else:
        return redirect('recommended_allocation')


# department head can customize the TA number
def ta_request_list(request):
    semester = request.session['semester']
    duty = TADuty.objects.filter(curriculum__semester=semester).order_by('curriculum__courseName')
    if duty.exists():
        return render(request, 'ta_request_list.html', {'taduty': duty})
    else:
        return HttpResponse('there is no course')


# get ta duty
# id: course id
def duty_all(request, id):
    ta_duty = TADuty.objects.get(curriculum_id=id)
    if request.method == 'GET':
        context = {
            'labNumber': ta_duty.labNumber,
            'preparationHour': ta_duty.preparationHour,
            'labHour': ta_duty.labHour,
            'labWorkingHour': ta_duty.labWorkingHour,
            'assignmentNumber': ta_duty.assignmentNumber,
            'assignmentWorkingHour': ta_duty.assignmentWorkingHour,
            'contactHour': ta_duty.contactHour,
            'otherDutiesHour': ta_duty.otherDutiesHour,
            'totalHour': ta_duty.totalHour,
            'recommendedTANumber': ta_duty.recommendedTANumber,
        }
        return JsonResponse(context)


@csrf_exempt
def update_positions(request):
    if request.method == "POST" and request.is_ajax():
        position = request.POST['positions']
        print(position)
        duty_id = request.POST['id']
        try:
            duty = TADuty.objects.get(id=duty_id)
            duty.recommendedTANumber = position
            print(duty.recommendedTANumber)
            duty.save()
            return HttpResponse(status=204)
        except TADuty.DoesNotExist:
            return JsonResponse({'error': 'something bad'}, status=400)

#TA page TA information edit
@csrf_exempt
def editTAInformation(request):
    if request.POST:
        data = request.POST['taInformation']
        username = request.session['username']
        User.objects.filter(username=username).update(email=data)
        return HttpResponse("success")

@csrf_exempt
#TA page pass course selected to database
def passTASelection(request):
    if request.POST:
        courseID = request.POST['courseID']
        userID = User.objects.get(username= request.session['username'])
        roleID = TA.objects.get(user_id=userID.id)
        courseRank = request.POST['courseRank']
        # delete course on that rank
        #init course Object??????

        try:
          courseObject = RankCourse.objects.get(TA_id=roleID.id,ranking=courseRank)
        except RankCourse.DoesNotExist:
            pass
        else:
          courseObject.delete()
        #also delete the previous course information
        try:
          courseObject = RankCourse.objects.get(TA_id=roleID.id,curriculum_id=courseID)
        except RankCourse.DoesNotExist:
          pass
        else:
          courseObject.delete()
        if courseRank is not '0':
            maxIndex = RankCourse.objects.all().aggregate(Max('rowid'))

            max = int(maxIndex['rowid__max']) + 1

            obj = RankCourse(
            rowid = max,
            id = max,
            ranking = courseRank,
            TA_id=roleID.id,
            curriculum_id=courseID
            )
            obj.save()
        return HttpResponse("success")

@csrf_exempt
#pass professor select TA from professor page
def passCourseSelection(request):
    if request.POST:
        taID = request.POST.getlist("taID[]")
        taRank = request.POST.getlist("taRank[]")
        courseID = request.POST.getlist("courseID[]")
        i=0

        for x in taID:
            # transfer course id to curriculum id
            curriculumID = Course.objects.get(courseName=courseID[i])
            # get TA object to insert to TA field

            if int(taID[i]) > 0:
                taObject = TA.objects.get(user_id=taID[i])
                #delete this TA former ranking in database
                try:
                    formerTARecord = RankTA.objects.get(TA_id=taObject.id,curriculum_id=curriculumID)
                except RankTA.DoesNotExist:
                    pass
                else:
                 formerTARecord.delete()
                #delete former rank of course in database
                try:
                 formerTARank = RankTA.objects.get(ranking=taRank[i],curriculum_id=curriculumID)
                except RankTA.DoesNotExist:
                     pass
                else:
                    formerTARank.delete()
                RankTA.objects.create(curriculum=curriculumID, TA=taObject, ranking=taRank[i])

            else:
                try:
                   formerTARank = RankTA.objects.get(ranking=taRank[i], curriculum_id=curriculumID)
                except RankTA.DoesNotExist:
                   pass
                else:
                   formerTARank.delete()


            i = i+1
        return HttpResponse("success")


def rankingFunction():
    try:
        delData = MatchResult.objects.filter()
    except MatchResult.DoesNotExist:
        pass
    else:
        delData.delete()
    #delete all exist data

    courseRank = RankCourse.objects.values('curriculum_id').annotate(count=Count('curriculum_id')).order_by('count')
    #set all course in list
    unrankedCourseLists = []
    rankedTAList = []
    for unrankedCourse in courseRank:
        unrankedCourseLists.append(unrankedCourse['curriculum_id'])

    for courseInRanking in courseRank:
        # directly assign the course which has < 2 number of TA choose
        if courseInRanking['count'] < 3:
            taRank = RankCourse.objects.filter(curriculum_id=courseInRanking['curriculum_id']).order_by('ranking')
            if taRank.exists():
                rankFlag = 1;
                for i in taRank:
                    MatchResult.objects.create(TARanking=rankFlag,TA_id=i.TA_id,curriculum_id=courseInRanking['curriculum_id'],courseRanking=rankFlag,positions=2,status=True)
                    rankFlag = rankFlag +1
                    rankedTAList.append(i.TA_id)
            unrankedCourseLists.remove(courseInRanking['curriculum_id'])
        #for other course

    scale = 2
    #set the range of for scale
    scale = int(RankCourse.objects.values('curriculum_id').count()) + int(RankTA.objects.values('TA_id').count())
    #for from 2 to scale
    for standardMatchValue in range(2,scale,1):
        #遍历所有课程
        print(unrankedCourseLists)
        for unrankedCourseID in unrankedCourseLists:
            if courseIsRanked(unrankedCourseID):
                unrankedCourseLists.remove(unrankedCourseID)

            else:
             unrankedCourseSelectTAObjectList = RankTA.objects.filter(curriculum_id=unrankedCourseID)
             for unrankedCourseSelectTAObject in unrankedCourseSelectTAObjectList:
                #itrate all possible TA
                if taIsRanked(unrankedCourseSelectTAObject.TA_id,rankedTAList):
                    pass
                #filter ranked TA
                else:
                 try:
                    unrankedTASelectCourseObject = RankCourse.objects.get(TA_id=unrankedCourseSelectTAObject.TA_id,curriculum_id=unrankedCourseID)
                 except RankCourse.DoesNotExist:
                    pass
                    #filter TA has not chose this course
                 else:
                    rankMark = int(unrankedTASelectCourseObject.ranking)+int(unrankedCourseSelectTAObject.ranking)
                    if rankMark <= standardMatchValue:

                        print(unrankedTASelectCourseObject.TA_id)
                        MatchResult.objects.create(TARanking=unrankedTASelectCourseObject.ranking, TA_id=unrankedTASelectCourseObject.TA_id,
                                                   curriculum_id=unrankedCourseSelectTAObject.curriculum_id,
                                                   courseRanking=unrankedCourseSelectTAObject.ranking, positions=2, status=True)
                        rankedTAList.append(unrankedTASelectCourseObject.TA_id)


    return 0

def taIsRanked(taID,rankedTAList):

    for i in rankedTAList:
        if int(taID) == int(i):
            return True
    return False

def courseIsRanked(courseID):
    if int(MatchResult.objects.filter(curriculum_id=courseID).count()) <1:
        return False
    else:
        courseCount = int(MatchResult.objects.filter(curriculum_id=courseID).count())
        if courseCount > 1:
            return True
        else:
            return False
