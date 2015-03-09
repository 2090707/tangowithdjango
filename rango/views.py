from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from models import UserProfile
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm, EditUserInfoForm
from datetime import datetime
from rango.bing_search import run_query
import json

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
    context_dict['result_list'] = None
    context_dict['query'] = None
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)
            context_dict['result_list'] = result_list
            context_dict['query'] = query

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
        context_dict['category_name_slug'] = category_name_slug

    except Category.DoesNotExist:
        return HttpResponse("<h2>The category you are trying to access does not exist!</h2><br />"+
                            "<a href='/rango/'>Index</a>")

    if not context_dict['query']:
        context_dict['query'] = category.name

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
    # check if category exists
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        # post request -> get a new form
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                # init page 'attributes'
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


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


def search(request):
    """Handles search functionality / queries via Bing"""
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})


def track_url(request):
    """Handles view count of each page"""
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                # fetch page and increment view count
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)

@login_required
def register_profile(request):
    if request.method == 'POST':
        profile_form = UserProfileForm(data=request.POST)

        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user

            # attach a picture
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # everything -> db
            profile.save()
            return redirect("/rango/")

        else:
            print profile_form.errors
    else:
        profile_form = UserProfileForm()
    return render(request, "rango/profile_registration.html", {'profile_form': profile_form})


@login_required
def edit_profile(request):
    """Handles user profile editing by fetching form data and altering the database"""
    context_dict = {}

    # alter db
    if request.method == 'POST':
        user_form = EditUserInfoForm(data=request.POST, instance=request.user)
        profile_form = UserProfileForm(data=request.POST, instance=request.user.userprofile)

        if profile_form.is_valid and user_form.is_valid:
            profile = profile_form.save(commit=False)
            user = profile_form.save(commit=False)
            # handle picture change
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # save changes
            user.save()
            profile.save()
        else:
            print user_form.errors
            print profile_form.errors
    else:
        user_form = EditUserInfoForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)

    context_dict['user_form'] = user_form
    context_dict['profile_form'] = profile_form
    context_dict['picture'] = request.user.userprofile.picture
    return render(request, "rango/profile.html", context_dict)


@login_required
def browse_profiles(request):
    all_users = User.objects.all()
    return render(request, 'rango/browse_profiles.html', {'users': all_users})


@login_required
def like_category(request):
    """handles the AJAX get requests which update the category likes"""
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            # increment likes and save to db
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()

    return HttpResponse(likes)


def get_category_list(max_results=0, starts_with=''):
    """Helper function which filters categories according to the starts_with string"""
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)

    # check results number
    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]

    return cat_list


def suggest_category(request):
    """returns a view of the top 8 matching results """
    cat_list = []
    starts_with = ''

    # get data
    if request.method == 'GET':
        starts_with = request.GET['suggestion']

    cat_list = get_category_list(8, starts_with)
    response = {}
    results = []

    # append categories from list to results list in format 'name / url / slug'
    for cat in cat_list:
        results.append({'name': cat.name, 'url': "/rango/category/" + cat.slug})
    response['data'] = results

    # json response containing results list
    return HttpResponse(json.dumps(results), content_type="application/json")
