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
    title = StringProperty(max_length=TITLE_MAX_LENGTH, required=True)
    
class Diagram(Category):
    category = RelationshipTo('Category', 'IN', cardinality=One)
    COMMUTES = { 'C' : 'Commutes', 'NC' : "Non-Commutative" }
    commutes = StringProperty(choices=COMMUTES)
    
    
