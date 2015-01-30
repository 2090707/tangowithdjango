from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category_list}
    context_dict['pages_by_views'] = Page.objects.order_by('-views')[0:5]

    return render(request, 'rango/index.html', context_dict)

def about(request):
    return render(request, 'rango/about.html', {})

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
