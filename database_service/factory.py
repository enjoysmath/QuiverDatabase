from .models import *


def get_unique(Model, **kwargs):
    """
    Queries a model and if it doesn't exist, creates with same args.
    For some reason `unique_index=True` everywhere does nothing.
    """
    node = Model.nodes.get_or_none(**kwargs)
    if node is None:
        node = Model(**kwargs)
        node.save()
    return node
    
    
def get_category(obs=None, **kwargs):
    """
    Queries a model and if it doesn't exist, creates with same args.
    For some reason `unique_index=True` everywhere does nothing.
    """
    cat = get_unique(Category, **kwargs)
    
    if obs:
        for ob in obs:
            #TODO may need to check if it's not already connected
            cat.objects.connect(ob)
        cat.save()
        
    return cat


def get_diagram(cat=None, obs=None, **kwargs):
    diagram = None
    
    if 'uid' in kwargs and 'uid' is not None:
        diagram = Diagram.nodes.get_or_none(**kwargs)
        del kwargs['uid']
        
    if diagram is None:
        diagram = Diagram(**kwargs).save()
        if cat is None:
            cat = get_category()
        elif isinstance(cat, dict):
            cat = get_category(**cat)
        #else we already have a category passed in
        
        diagram.category.connect(cat)
        diagram.save()
    
    if obs:
        for ob in obs:  
            diagram.objects.connect(ob)
        diagram.save()
        
    return diagram