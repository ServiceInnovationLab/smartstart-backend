import os
from functools import wraps
from django.shortcuts import render_to_response


def render_to(template_name=None, content_type=None, status=None, using=None):
    """
    A modified version for django-annoying render_to.
    """
    def renderer(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            context = function(request, *args, **kwargs)
            if not isinstance(context, dict):
                return context
            tmpl = context.pop('TEMPLATE', template_name)
            if tmpl is None:
                template_dir = os.path.join(*function.__module__.split('.')[:-1])
                tmpl = '{}/{}.html'.format(template_dir, function.func_name)
            return render_to_response(
                tmpl,
                context=context,
                content_type=content_type,
                status=status,
                using=using
            )
        return wrapper
    return renderer
