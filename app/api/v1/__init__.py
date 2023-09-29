from flask_smorest import Blueprint


def register_api_blueprints(app):
    from .plate import blp as plate_blp
    from .section import blp as section_blp
    from .cell import blp as cell_blp
    from .item import blp as item_blp
    from .stack import blp as stack_blp
    from .compound import blp as compound_blp
    from .timepoint import blp as timepoint_blp
    from .modality import blp as modality_blp
    from .tag import blp as tag_blp

    api_blp = Blueprint("Api", "Api", url_prefix="/api/v1")

    api_blp.register_blueprint(plate_blp)
    api_blp.register_blueprint(section_blp)
    api_blp.register_blueprint(cell_blp)
    api_blp.register_blueprint(item_blp)
    api_blp.register_blueprint(compound_blp)
    api_blp.register_blueprint(stack_blp)
    api_blp.register_blueprint(timepoint_blp)
    api_blp.register_blueprint(modality_blp)
    api_blp.register_blueprint(tag_blp)

    app.register_blueprint(api_blp)
