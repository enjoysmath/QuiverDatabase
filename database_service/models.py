from django.db import models
from neomodel import *
from django_neomodel import DjangoNode
from QuiverDatabase.settings import MAX_NAME_LENGTH

# Create your models here.


class Morphism(StructuredRel):
    name = StringProperty(max_length=MAX_NAME_LENGTH, required=True)

    
class Functor(Morphism):
    pass


class Object(StructuredNode):
    uid = UniqueIdProperty()
    morphisms = RelationshipTo('Object', 'MAPS_TO', model=Morphism)
    name = StringProperty(max_length=MAX_NAME_LENGTH, required=True)
    
    
class Category(Object):
    objects = RelationshipTo('Object', 'CONTAINS')
    name = StringProperty(max_length=MAX_NAME_LENGTH, required=True)
        
        
class Diagram(Category):
    category = RelationshipTo('Category', 'IN', cardinality=One)
    COMMUTES = { 'C' : 'Commutes', 'NC' : "Non-Commutative" }
    commutes = StringProperty(choices=COMMUTES)
    
    
