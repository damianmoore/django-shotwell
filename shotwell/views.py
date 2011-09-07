from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.conf import settings
import os
import sqlite3
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import shutil
from PIL import Image


def gallery(request):
    context = {}
    db_file = os.path.join(settings.SHOTWELL_CONFIG_DIR, 'data', 'photo.db')
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    old_rows = c.execute('SELECT id, filename FROM phototable WHERE flags=0 ORDER BY timestamp DESC;')
    new_rows = []
    for (id, filename) in old_rows:
        thumb_fn = 'thumb%016x.jpg' % id
        new_rows.append([id, filename, thumb_fn])

    paginator = Paginator(new_rows, 25)
    page = request.GET.get('page', 1)
    try:
        photos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        photos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        photos = paginator.page(paginator.num_pages)
    context['photos'] = photos
    context['thumb_media'] = settings.SHOTWELL_THUMB_MEDIA
    return render_to_response('shotwell/gallery.html', context)


def photo(request, photo_id):
    context = {}
    db_file = os.path.join(settings.SHOTWELL_CONFIG_DIR, 'data', 'photo.db')
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('SELECT id, filename FROM phototable WHERE id=%s LIMIT 1;' % photo_id)
    #context['photo'] = c.fetchone()
    context['photo'] = list(c.fetchone())
    context['photo'].append('thumb%016x.jpg' % context['photo'][0])
    context['thumb_media'] = settings.SHOTWELL_THUMB_MEDIA
    return render_to_response('shotwell/photo.html', context)


def api_photo(request, photo_id):
    db_file = os.path.join(settings.SHOTWELL_CONFIG_DIR, 'data', 'photo.db')
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('SELECT id, filename FROM phototable WHERE id=%s LIMIT 1;' % photo_id)
    photo = c.fetchone()

    max_size = request.GET.get('max-size', None)
    if max_size:
        max_size = int(max_size)
        if max_size > 2000:
            max_size = None
        img_fn = '%s_%d.jpg' % (photo_id, max_size)
        im = Image.open(photo[1])
        im.thumbnail((max_size, max_size))
        im.save(os.path.join(settings.SHOTWELL_TEMP_DIR, img_fn))
    else:
        img_fn = '%s.jpg' % photo_id
        shutil.copyfile(photo[1], os.path.join(settings.SHOTWELL_TEMP_DIR, img_fn))
    return HttpResponseRedirect('%s%s' % (settings.SHOTWELL_TEMP_MEDIA, img_fn))
        
    
