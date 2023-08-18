#!/usr/bin/env python3

from flask import (Blueprint, Markup, flash, redirect, render_template,
                   render_template_string, request, session, url_for)
from flask_flatpages import pygments_style_defs

from .. import pages

bp = Blueprint("index", __name__, template_folder="templates", static_folder="static")


@bp.route("/pygments.css")
def pygments_css():
    return pygments_style_defs("emacs"), 200, {"Content-Type": "text/css"}


@bp.route("/ping")
def get():
    return {"success": True, "message": "healthy"}


@bp.route("/")
def index():
    return redirect(url_for('plate_list'))

    # page = pages.get_or_404("index")
    # template = page.meta.get("template", "flatpage.html")
    # return render_template(template, page=page)


@bp.route("/pages/<path:path>")
def page(path=None):
    page = pages.get_or_404(path)
    page.body = render_template_string(page.body)
    template = page.meta.get("template", "flatpage.html")
    return render_template(template, page=page)
