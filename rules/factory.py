from .models import *


def get_rule_by_id(rule_id=None, key=None, key_cat=None, res=None, res_cat=None, **kwargs):
    #rule = None

    #if rule_id is not None:
        #rule = DiagramRule.nodes.get_or_none(uid=rule_id)

    #if rule is None or rule_id is None:
        #rule = get_rule(key, key_cat, res, res_cat, **kwargs)
    
    #return rule
    return None


def get_rule(key=None, key_cat=None, res=None, res_cat=None, **kwargs):
    return None
    #rule = None
    
    #if 'name' not in kwargs:
        #kwargs['name'] = 'Rule'
    #if key is None:
        #key = {'name' : 'Key Diagram'}
    #if key_cat is None:
        #key_cat = {'name' : 'Any'}
    #if res is None:
        #res = {'name' : 'Result Diagram'}
    #if res_cat is None:
        #res_cat = {'name' : 'Any'}
    
    #if 'uid' in kwargs:
        #rule = DiagramRule.nodes.get_or_none(**kwargs)
        #del kwargs['uid']  # Don't pass into next creation code (where it is randomly generated)
    
    #if rule is None:        
        #if 'title' not in kwargs:
            #kwargs['title'] = 'Rule Title'        
        #rule = DiagramRule(**kwargs)
        #rule.save()
        #key_cat = get_category(**key_cat)
        #key_diagram = get_diagram(cat=key_cat, **key)
        #rule.key_diagram.connect(key_diagram)
        #res_cat = get_category(**res_cat)
        #res_diagram = get_diagram(cat=res_cat, **res)
        #rule.result_diagram.connect(res_diagram)
        #rule.save()    
    
    #return rule


    
