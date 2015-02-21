from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from datetime import datetime

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category_list}
    context_dict['pages_by_views'] = Page.objects.order_by('-views')[0:5]

    # get number of visits to the site
    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False
    context_dict['visits'] = visits

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        # if it's been more than a day since last visit
        if(datetime.now() - last_visit_time).days > 0:
            visits = visits + 1
            reset_last_visit_time = True
    else:
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
        context_dict['visits'] = visits

    response = render(request, 'rango/index.html', context_dict)

    return response

def about(request):
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0

    return render(request, 'rango/about.html', {'visits' : count})

def category(request, category_name_slug):
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        
        pages = Page.objects.filter(category=category)

        context_dict['pages'] = pages
        context_dict['category'] = category
        context_dict['category_name_slug'] = category_name_slug

    except Category.DoesNotExist:
        return HttpResponse("<h2>The category you are trying to access does not exist!</h2><br />"+
                            "<a href='/rango/'>Index</a>")

    return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request):
    # is it a POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # is the form valid?
        if form.is_valid():
            # save new category to db
            form.save(commit=True)
            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()

    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
            return HttpResponse("<h2>You have successfully added the new page!</h2>"+
                                "<a href='/rango/'>Index</a>")
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form':form, 'category':cat, 'category_name_slug':category_name_slug}

    return render(request, 'rango/add_page.html', context_dict)


#def register(request):
#    context_dict = {}
    # successful registration flag
#    registered = False
#
#    if request.method == 'POST':
        # grab info from the raw form
#        user_form = UserForm(data=request.POST)
#        profile_form = UserProfileForm(data=request.POST)
#
        # both forms are valid?
#        if user_form.is_valid() and profile_form.is_valid():
            # save user's form data to the db
#            user = user_form.save()

            # hash password
#            user.set_password(user.password)
#            user.save()

            # sort out the UserProfile instance
#            profile = profile_form.save(commit=False)
#            profile.user = user
#
            # was there a picture provided?
#            if 'picture' in request.FILES:
#                profile.picture = request.FILES['picture']
#
#            profile.save()
#            registered = True
#
#        else:
#            print user_form.errors, profile_form.errors
#
#    else:
#        user_form = UserForm()
#        profile_form = UserProfileForm()
#
#    context_dict['user_form'] = user_form
#    context_dict['profile_form'] = profile_form
#    context_dict['registered'] = registered
#    return render(request,
#                  'rango/register.html',
#                  context_dict,)
#
#def user_login(request):
#    
#    if request.method == 'POST':
#        username = request.POST['username']
#        password = request.POST['password']
#
        # check if name/pass combination is valid -> user object
#        user = authenticate(username=username, password=password)
#
#        if user:
#            if user.is_active:
#                login(request, user)
#                return HttpResponseRedirect('/rango/')
#            else:
#                return HttpResponse("Your Rango account is disabled.")
#        else:
#            print "Invalid login details: {0}, {1}".format(username, password)
            #return HttpResponse("Invalid login details supplied.<br /><a href='/rango/login'>Try again</a>")
#            return render(request, 'rango/login.html', {'bad_attempt': True})
#
#    else:
#        return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


#@login_required
#def user_logout(request):
#    logout(request)
#    return HttpResponseRedirect('/rango/')
