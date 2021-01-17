from django.db import models
from neomodel import *
from django_neomodel import DjangoNode
from QuiverDatabase.settings import NAME_MAX_LENGTH, TITLE_MAX_LENGTH

# Create your models here.


class Morphism(StructuredRel):
    name = StringProperty(max_length=NAME_MAX_LENGTH, required=True)

    
class Functor(Morphism):
    pass


class Object(StructuredNode):
    morphisms = RelationshipTo('Object', 'MAPS_TO', model=Morphism)
    name = StringProperty(max_length=NAME_MAX_LENGTH, required=True)
    
    
class Category(Object):
    objects = RelationshipTo('Object', 'CONTAINS')
    name = StringProperty(max_length=NAME_MAX_LENGTH, required=True)
        
        
class Diagram(Category):
    category = RelationshipTo('Category', 'IN', cardinality=One)
    COMMUTES = { 'C' : 'Commutes', 'NC' : "Non-Commutative" }
    commutes = StringProperty(choices=COMMUTES)
    
    
def unique(Model, **kwargs):
    """
    Queries a model and if it doesn't exist, creates with same args.
    For some reason `unique_index=True` everywhere does nothing.
    """
    node = Model.nodes.get_or_none(**kwargs)
    if node is None:
        node = Model(**kwargs)
    return node
    