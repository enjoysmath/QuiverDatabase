from django.db import models
from neomodel import *
from django_neomodel import DjangoNode
from QuiverDatabase.settings import MAX_NAME_LENGTH
from database_service.models import Diagram

# Create your models here.

class DiagramRule(StructuredNode):
    uid = UniqueIdProperty()
    title = StringProperty(max_length=MAX_NAME_LENGTH, required=True)
    key_diagram = RelationshipTo('Diagram', 'KEY', cardinality=One)
    result_diagram = RelationshipTo('Diagram', 'RESULT', cardinality=One)
    

#class Morphism(StructuredRel):
    #name = StringProperty(max_length=NAME_MAX_LENGTH, required=True)
    
#class Functor(Morphism):
    #pass

#class Object(StructuredNode):
    #category = RelationshipTo('Category', 'IN', cardinality=One)
    #morphisms = RelationshipTo('Object', 'MAPS_TO', model=Morphism)
    #name = StringProperty(max_length=NAME_MAX_LENGTH, required=True)
    
    #class Meta:
        #app_label = 'category'     #? TODO (how do Django forms work?)
    
#class Category(Object):
    #objects = RelationshipTo('Object', 'CONTAINS')
    

    
