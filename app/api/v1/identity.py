#!/usr/bin/env python

from app.api import Blueprint
from flask import request
from flask.views import MethodView

from . import get_user_profile

blp = Blueprint("Identity", "Identity", url_prefix="/api/v1/identity", description="")


@blp.route("/")
class IdentityAPI(MethodView):

    @blp.response(200, content_type='application/json')
    def get(self):
        """Get identity of caller with entitlements"""

        user_profile = get_user_profile(request)

        if user_profile:
            return (user_profile, 200)
        return ('No user profile found', 500)
