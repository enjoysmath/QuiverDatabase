from .models import *
from database_service.factory import get_diagram, get_category

def get_rule_by_id(rule_id, key, key_cat, res, res_cat, **kwargs):
    rule = None
    
    if rule_id is not None:
        rule = DiagramRule.nodes.get_or_none(uid=rule_id)

    if rule is None or rule_id is None:
        rule = get_rule(key, key_cat, res, res_cat, **kwargs)
    
    return rule


def get_rule(key, key_cat, res, res_cat, **kwargs):
    rule = None
    
    if 'uid' in kwargs:
        rule = DiagramRule.nodes.get_or_none(**kwargs)
        del kwargs['uid']  # Don't pass into next creation code (where it is randomly generated)
    
    if rule is None:        
        rule = DiagramRule(**kwargs)
        rule.save()
        key_cat = get_category(**key_cat)
        key_diagram = get_diagram(cat=key_cat, **key)
        rule.key_diagram.connect(key_diagram)
        res_cat = get_category(**res_cat)
        res_diagram = get_diagram(cat=res_cat, **res)
        rule.result_diagram.connect(res_diagram)
        rule.save()    
    
    return rule


    
