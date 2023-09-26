#!/usr/bin/env python3
from src import create_app, db
import pandas as pd
import json
from rich import print

app = create_app('prod')

from src.models.compound import Compound, CompoundProperty, CompoundPropertyType

with app.app_context():
    cpds = db.session.query(Compound).all()
    props = []
    for c in cpds:
        props.append({'moa_group': c.moa_group,
                      'moa_subgroup': c.moa_subgroup,
                      'target': c.target})

    props = set([json.dumps(d) for d in props])
    props = [json.loads(d) for d in props]

    moa_groups = list(set([p['moa_group'] for p in props]))
    moa_groups = [g for g in moa_groups if g]
    tree = {}
    for group in moa_groups:
        subgroups = list(set([p['moa_subgroup'] for p in props if p['moa_group'] == group]))
        subgroups = [sg for sg in subgroups if sg]
        tree[group] = {}
        for subgroup in subgroups:
            targets = list(set([p['target'] for p in props
                                if (p['moa_subgroup'] == subgroup) & (p['moa_group'] == group)]))
            targets = [t for t in targets if t]
            tree[group][subgroup] = targets

    print(tree)

    db.session.query(CompoundProperty).delete()
    db.session.execute("ALTER SEQUENCE compound_property_id_seq RESTART WITH 1")
    db.session.commit()
    for tree_id, group in enumerate(tree.keys()):
        group_prop = CompoundProperty(type=CompoundPropertyType.moa_group, value=group,
                                      tree_id=tree_id+1)
        db.session.add(group_prop)
        db.session.commit()

        for subgroup in tree[group].keys():
            subgroup_prop = CompoundProperty(type=CompoundPropertyType.moa_subgroup, value=subgroup,
                                             tree_id=group_prop.tree_id, parent_id=group_prop.id)
            db.session.add(subgroup_prop)
            db.session.commit()

            for target in tree[group][subgroup]:
                target_prop = CompoundProperty(type=CompoundPropertyType.target, value=target,
                                               tree_id=subgroup_prop.tree_id, parent_id=subgroup_prop.id)
                db.session.add(target_prop)
                db.session.commit()

    empty = CompoundProperty(type='moa_group', value='')
    db.session.add(empty)
    db.session.commit()

    empty_prop = db.session.query(CompoundProperty).filter_by(type='moa_group',
                                                                    value='').first()
    for cpd in db.session.query(Compound).all():
        cpd.property_id = empty_prop.id
        db.session.commit()
        for field in ['target', 'moa_subgroup', 'moa_group']:
            value = getattr(cpd, field)
            if value:
                prop = db.session.query(CompoundProperty).filter_by(type=field,
                                                                    value=value).first()
                cpd.property_id = prop.id
                db.session.commit()
                break
