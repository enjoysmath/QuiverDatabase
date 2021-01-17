from crispy_forms.templatetags.crispy_forms_filters import as_crispy_form # this line is different

from django.contrib import messages
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.utils import translation
from jinja2 import Environment


def environment(**options):
    env = Environment(
        extensions=["jinja2.ext.i18n", "jinja2.ext.with_"], **options
    )
    env.globals.update(
        {
            "get_messages": messages.get_messages,
            "static": staticfiles_storage.url,
            "crispy": as_crispy_form,  # this line is different
            "url": reverse,
        }
    )
    env.install_gettext_translations(translation)
    return env