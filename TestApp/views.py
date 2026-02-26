from django.shortcuts import render, redirect
from .models import Person, TestResult, TestModule, Question, Answer
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt

# - - - - - -  - - -- -  - - -  LOGIN - -  - - - - - --  -- - - - 
from django.db.models import Avg, Max
@csrf_exempt
def login(request):
    html = "login.html"
    if request.method == "POST":
        login_input = request.POST.get("login")
        password_input = request.POST.get("password")

        try:
            # QuerySet emas, bitta foydalanuvchini olish uchun .get ishlatamiz
            user = Person.objects.get(login=login_input)

            if user.role == 'admin':
                return redirect(f"/admin/user/admin_user_profile/{user.id}/")

            elif check_password(password_input, user.password):
                request.session["user_id"] = user.id
                return redirect("TestApp:dashboard")
            else:
                return render(request, html, {"error": "Parol noto‘g‘ri"})

        except Person.DoesNotExist:
            return render(request, html, {"error": "Foydalanuvchi topilmadi"})

    return render(request, html)
# - - -  - -- - - -  --  - - - - - - -- - - - - - - - --  - -- -  -
@csrf_exempt
def admin_reqiured(views_func):
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get("user_id")

        if not user_id:
            return redirect("TestApp:signup")
        user = Person.objects.get(id = user_id)

        if not user.is_admin:
            return redirect("TestApp:dashboard")
        
        return views_func(request, *args, **kwargs)
    return wrapper

@csrf_exempt
@admin_reqiured
def admin_dashboard(request):
    search = request.GET.get("q")

    users = Person.objects.filter(is_admin = False)

    if search:
        users = users.filter(name__icontains = search)
    users = users.order_by("name")

    return render(request, "admin/dashboard.html", {
        "users" : users
    })


@csrf_exempt
def admin_user_profile(request, user_id):
    user = Person.objects.get(id=user_id)
    results = TestResult.objects.filter(user=user)

    return render(request, "user_profile.html", {
        "profile_user": user,
        "results": results
    })

@csrf_exempt
def admin_dashboard(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("TestApp:login")

    user = Person.objects.get(id=user_id)

    if user.role != 'admin':
        return redirect("TestApp:dashboard")

    users = Person.objects.all()
    modules = TestModule.objects.all()

    context = {
        "user": user,
        "users": users,
        "modules": modules
    }

    return render(request, "admin_d.html", context)

# -------- - - - - - - - Register - - - -- - -  - - - - - - - -
@csrf_exempt
def give_admin(request, user_id):
    user = Person.objects.get(id = user_id)
    user.is_admin = True
    user.save()

def signin(request):
    if request.method == "POST":
        name = request.POST.get("name")
        login = request.POST.get("login")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "signin.html", {"error": "Parollar mos emas"})

        if Person.objects.filter(login=login).exists():
            return render(request, "signin.html", {"error": "Login band"})

        Person.objects.create(
            name=name,
            login=login,
            password=make_password(password)
        )

        return redirect("TestApp:dashboard")

    return render(request, "signin.html")
# - - --  - - - - - - - - --  - - -  - - - -  - - - - - - -- 
@csrf_exempt
def logout_view(request):
    request.session.flush()
    return redirect("TestApp:home")
@csrf_exempt
def home(request):
    if request.session.get("user_id"):
        return redirect("TestApp:dashboard")
    return render(request, "home.html", {})
@csrf_exempt
# Dashboard
def user_dashboard(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("TestApp:signup")
    user = Person.objects.get(id = user_id)

    # Dashboard qism sozlanmasi

    test_results = TestResult.objects.filter(user = user)
    total_tests = test_results.count()
    avg_score = round(sum([r.score for r in test_results])/total_tests,2) if total_tests>0 else 0
    resent_results = test_results.order_by('-id')[:5]
    modules = TestModule.objects.all()
    soni = modules.count()
    context = {
        "soni" : soni,
        "modules": modules,
        "user" : user,
        "total_tests" : total_tests,
        "avg_score":avg_score,
        "recent_results":resent_results,
    }
    
    return render(request, "dashboard.html", context)




@csrf_exempt
def admin_dashboard(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("TestApp:login")

    user = Person.objects.get(id=user_id)

    if user.role != 'admin':
        return redirect("TestApp:dashboard")

    users = Person.objects.all()
    modules = TestModule.objects.all()

    context = {
        "user": user,
        "users": users,
        "modules": modules
    }

    return render(request, "admin/dashboard.html", context)


@csrf_exempt
# Tests@csrf_exempt
def tests(request):
    
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("TestApp:signup")
    user = Person.objects.get(id = user_id)

    # Modullar summ
    user = Person.objects.all()
    modules = TestModule.objects.all()
    context = {"modules":modules, "user":user,}
    return render(request, "tests.html", context)

@csrf_exempt
def start_test(request, module_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("TestApp:signup")

    module = TestModule.objects.get(id=module_id)
    questions = module.question_set.all()

    if request.method == "POST":
        correct = 0

        for question in questions:
            selected = request.POST.get(f"question_{question.id}")
            if selected:
                answer = Answer.objects.get(id=selected)
                if answer.is_correct:
                    correct += 1

        score = round((correct / questions.count()) * 100, 2)

        TestResult.objects.create(
            user_id=user_id,
            module=module,
            score=score
        )

        return redirect("TestApp:my_result")

    return render(request, "question.html", {
        "module": module,
        "questions": questions
    })

    

@csrf_exempt
def my_result(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("TestApp:signup")
    user = Person.objects.get(id = user_id)
    results = TestResult.objects.filter(user = user).order_by("-date")

    total_tests = results.count()

    stats = results.aggregate(
        avg_score = Avg("score"),
        best_score = Max("score")
    )    

    avg_score = round(stats["avg_score"], 2) if stats["avg_score"] else 0
    best_score = stats["best_score"] if stats["best_score"] else 0

    last_result = results.first()
    last_score = last_result.score if last_result else 0
    
    context = {
        "user":user,
        "total_stets" : total_tests,
        "avg_score":avg_score,
        "best_score":best_score,
        "last_score":last_score,
        "results":results
    }
    return render(request, "my-result.html", context)



@csrf_exempt
def profile(self):
    user_id = self.session.get('user_id')
    if not user_id:
        return redirect("TestApp:signup")
    user = Person.objects.get(id = user_id)

    if self.method == "POST":
        new_name = self.POST.get("name")
        new_login = self.POST.get("login")
        if new_name: user.name = new_name
        if new_login: user.login = new_login
        user.save()
        return redirect("TestApp:profile")
    
    
    test_results = TestResult.objects.filter(user=user)
    total_tests = test_results.count()
    avg_score = round(sum([r.score for r in test_results])/total_tests,2) if total_tests>0 else 0
    context = {
        "user":user,
        "total_tests" : total_tests,
        "avg_score":avg_score,
    }
    return render(self, "profile.html", context)
