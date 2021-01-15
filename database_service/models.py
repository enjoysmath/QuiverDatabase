from django.db import models
from neomodel import *
from django_neomodel import DjangoNode

NAME_MAX_LENGTH = 100

# Create your models here.


class Morphism(StructuredRel):
    name = StringProperty(max_length=NAME_MAX_LENGTH, required=True)
    
class Functor(Morphism):
    pass

class Object(StructuredNode):
    category = RelationshipTo('Category', 'IN', cardinality=One)
    morphisms = RelationshipTo('Object', 'MAPS_TO', model=Morphism)
    name = StringProperty(max_length=NAME_MAX_LENGTH, required=True)
    
    class Meta:
        app_label = 'category'     #? TODO (how do Django forms work?)
    
class Category(Object):
    objects = RelationshipTo('Object', 'CONTAINS')
    

    
