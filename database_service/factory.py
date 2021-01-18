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

    
def get_diagram(cat, obs=None, **kwargs):
    diagram = Diagram(**kwargs).save()
    diagram.category.connect(cat)
    
    if obs:
        for ob in obs:  
            diagram.objects.connect(ob)
    
    diagram.save()
        
    return diagram