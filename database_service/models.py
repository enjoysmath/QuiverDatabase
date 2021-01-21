from django.db import models
from neomodel import *
from django_neomodel import DjangoNode
from QuiverDatabase.settings import MAX_TEXT_LENGTH
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.

class Model:
    @staticmethod
    def our_create(**kwargs):
        raise NotImplementedError
    
    def copy_relations_from(self, old):
        raise NotImplementedError
    
    
class Morphism(StructuredRel):
    name = StringProperty(max_length=MAX_TEXT_LENGTH, required=True)
        
        
class Functor(Morphism):
    pass


class Object(StructuredNode, Model):
    uid = UniqueIdProperty()
    morphisms = RelationshipTo('Object', 'MAPS_TO', model=Morphism)
    name = StringProperty(max_length=MAX_TEXT_LENGTH, required=True)
    
    @staticmethod
    def our_create(**kwargs):
        object = Object(**kwargs).save()
        return object
    
    def copy_relations_from(self, old):
        for f in old.morphisms:
            self.morphisms.connect(f.end_node())   
        self.save()
    
    
class Category(Object):
    objects = RelationshipTo('Object', 'CONTAINS')
    name = StringProperty(max_length=MAX_TEXT_LENGTH, required=True)
    
    @staticmethod
    def our_create(**kwargs):
        category = Category(**kwargs).save()
        return category
                
    def copy_relations_from(self, old):
        for x in old.objects:
            self.objects.connect(x.end_node())
        self.save()
            
        
class Diagram(Category):
    category = RelationshipTo('Category', 'IN', cardinality=One)
    COMMUTES = { 'C' : 'Commutes', 'NC' : "Non-Commutative" }
    commutes = StringProperty(choices=COMMUTES)
    checked_out_by = StringProperty(max_length=MAX_TEXT_LENGTH)
    
    @staticmethod
    def our_create(**kwargs):
        diagram = Diagram(**kwargs).save()
        category = get_unique(Category, name='Any')
        diagram.category.connect(category)
        diagram.save()  
        return diagram
        
    def copy_relations_from(self, old):
        self.category.connect(old.category.single())
        self.checked_out_by = old.checked_out_by
        self.commutes = old.commutes
        self.save()
    
    
class Rule(Object):
    uid = UniqueIdProperty()
    key_diagram = RelationshipTo('Diagram', 'KEY', cardinality=One)
    result_diagram = RelationshipTo('Diagram', 'RESULT', cardinality=One)
    checked_out_by = StringProperty(max_length=MAX_TEXT_LENGTH)
    
    @staticmethod
    def our_create(**kwargs):
        rule = Rule(**kwargs).save()
        rule.key_diagram.connect(Diagram(name='').save())
        rule.result_diagram.connect(Diagram(name='').save())
        rule.save()
        return rule
    
    def transfer_from(self, old):
        self.key_diagram.connect(old.key_diagram.single())
        self.result_diagram.connect(old.result_diagram.single())
        self.checked_out_by = old.checked_out_by
        self.save()
        

model_str_to_class = {
    'Category' : Category,
    'Object' : Object,
    'Diagram' : Diagram,
    'Rule' : Rule,
}

MAX_MODEL_CLASS_NAME_LENGTH = max([len(x) for x in model_str_to_class.keys()])

def get_model_class(Model:str):
    if len(Model) > MAX_MODEL_CLASS_NAME_LENGTH:
        return ValueError("You're passing in an unimplemented Model string.")        
    
    if Model not in model_str_to_class:
        raise NotImplementedError(f'Model {Model} has no entry in a certain table.')
    
    Model = model_str_to_class[Model]    
    return Model


def get_model_by_uid(Model, uid:str):
    if len(uid) > 36:
        raise ValueError('That id is longer than a UUID4 is supposed to be.')
    
    if isinstance(Model, str):
        Model = get_model_class(Model)
        
    model = Model.nodes.get_or_none(uid=uid)    
    
    if model is None:
        raise ObjectDoesNotExist(f'An instance of the model {Model} with uid "{uid}" does not exist.')
    
    return model
                    
                    
def get_unique(Model, **kwargs):
    model = Model.nodes.get_or_none(**kwargs)
    
    if model is None:
        model = Model(**kwargs)
        model.save()
        
    return model