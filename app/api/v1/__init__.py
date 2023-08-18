import json
from functools import wraps

from flask import jsonify, make_response, request, current_app
from flask_smorest import abort


def check_dependencies(model, value, field:str, remote:str):

    item = model.query.filter_by(**{field: value}).first()

    if len(getattr(item, remote)) > 0:
        return abort(
            424,
            message="Found parent {} for item of type {} with {}: {}".format(
                remote, model.__name__, field, value
            ),
        )


def check_duplicate(session, model, **kwargs):
    """Abort if DB contains a specified element

    Parameters
    ----------
    session : SQLAlchemy session
    model : SQLAlchemy ORM object
    **kwargs: Specifies fields and values used for filtering
    """

    instance = session.query(model).filter_by(**kwargs).first()
    if instance is not None:
        abort(
            424,
            message="Found duplicate item of type {} with fields: {}, id: {}".format(
                model.__name__, str(kwargs), instance.id
            ),
        )


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


def get_user_profile(request):
    """
    Retrieve information about the user from Ocelot's header
    """
    out = {}
    if "user-profile" in request.headers:
        out = {**out, **json.loads(request.headers.get("user-profile"))}
    if "client-id" in request.headers:
        out = {**out, "client-id": request.headers.get("client-id")}
    if "user-id" in request.headers:
        out = {**out, "user-id": request.headers.get("user-id")}
    if out:
        return out

    return None


# Authentication decorator
def admin_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if current_app.config['TESTING']:
            return f(*args, **kwargs)

        user_profile = get_user_profile(request)
        if user_profile is not None:
            if "admin" in user_profile["entitlements"][current_app.config['APP_NAME']]:
                return f(*args, **kwargs)
        return make_response(
            jsonify(
                "You do not have the necessary entitlement(s) to perform this operation."
            ),
            500,
        )

    return decorator
