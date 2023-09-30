
def register_api_blueprints(restapi):

    from .plate import blp as plate_blp
    from .section import blp as section_blp
    from .cell import blp as cell_blp
    from .item import blp as item_blp
    from .stack import blp as stack_blp
    from .compound import blp as compound_blp
    from .timepoint import blp as timepoint_blp
    from .modality import blp as modality_blp
    from .tag import blp as tag_blp
    from .compound_props import blp as prop_blp

    restapi.register_blueprint(plate_blp)
    restapi.register_blueprint(section_blp)
    restapi.register_blueprint(cell_blp)
    restapi.register_blueprint(item_blp)
    restapi.register_blueprint(compound_blp)
    restapi.register_blueprint(stack_blp)
    restapi.register_blueprint(timepoint_blp)
    restapi.register_blueprint(modality_blp)
    restapi.register_blueprint(tag_blp)
    restapi.register_blueprint(prop_blp)
