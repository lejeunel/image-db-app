#!/usr/bin/env python

from flask.views import MethodView
from flask_smorest import Blueprint, abort
import json
from . import get_user_profile
from flask import request

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
