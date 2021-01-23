from django.db import models
from neomodel import *
from django_neomodel import DjangoNode
from QuiverDatabase.settings import MAX_TEXT_LENGTH
from django.core.exceptions import ObjectDoesNotExist
import database_service.quiver_data_format as fmt

# Create your models here.

class Model:
    @staticmethod
    def our_create(**kwargs):
        raise NotImplementedError
    
    def copy_relations_from(self, old):
        raise NotImplementedError
    
    
class Morphism(StructuredRel):
    #uid = StringProperty(default=Morphism.get_unique_id())
    name = StringProperty(max_length=MAX_TEXT_LENGTH, required=True)
    
    # RE-DESIGN: TODO - these need to be independent of style and settable in an accompanying
    # panel to the editor.
    # These are the mathematical properties, that you can search by:
    #epic = BooleanProperty(default=False)
    #monic = BooleanProperty(default=False)
    #inclusion = BooleanProperty(default=False)
    functor = BooleanProperty(default=False)
    
    # Strictly style below this line:   
    NUM_LINES = { 1: 'one', 2: 'two', 3: 'three' }
    num_lines = IntegerProperty(choices=NUM_LINES, default=1)
     
    ALIGNMENT = { 0:fmt.LeftAlign,  1:fmt.RightAlign, 2: fmt.CenterAlign, 3:fmt.OverAlign}
    alignment = IntegerProperty(choices=ALIGNMENT, default=fmt.DefaultAlignment)
    
    position = IntegerProperty(default=50)
    offset = IntegerProperty(default=0)
    curve = IntegerProperty(default=0)
    tail_shorten = IntegerProperty(default=0)
    head_shorten = IntegerProperty(default=0)
    
    TAIL_STYLE = {0:'none', 1:'mono', 2:'hook', 3:'arrowhead', 4:'maps_to'}
    tail_style = IntegerProperty(choices=TAIL_STYLE, default=0)
        
    SIDE = {0:'none', 1:'top', 2:'bottom'}
    hook_tail_side = IntegerProperty(choices=SIDE, default=0)    
    
    HEAD_STYLE = {0:'none', 1:'arrowhead', 2:'epi', 3:'harpoon'}
    head_style = IntegerProperty(choices=HEAD_STYLE, default=0)
    harpoon_head_side = IntegerProperty(choices=SIDE, default=0)
    
    BODY_STYLE = {0:'solid', 1:'none', 2:'dashed', 3:'dotted', 4:'squiggly', 5:'barred'}
    body_style = IntegerProperty(choices=BODY_STYLE, default=0)
    
    color_hue = IntegerProperty(default=0)
    color_sat = IntegerProperty(default=0)
    color_lum = IntegerProperty(default=0)
    color_alph = FloatProperty(default=1.0)
    
    def load_from_editor(self, edge):
        self.alignment = edge.alignment
        
        options = edge.options.dict
        self.position = options['label_position']
        self.offset = options['offset']
        self.curve = options['curve']
        self.tail_shorten = options['length_shorten']['source']
        self.head_shorten = options['length_shorten']['target']
        self.num_lines = options['level']
        
        self.body_style = next(x for x,y in self.BODY_STYLE.items() \
                               if y == options['style']['body']['name'])                
        
        self.tail_style = next(x for x,y in self.TAIL_STYLE.items() \
                               if y == options['style']['tail']['name'])
        
        if self.tail_style == 'hook':
            self.hook_tail_side = next(x for x,y in self.SIDE.items() \
                                       if y == options['style']['tail']['side'])
        
        self.head_style = next(x for x,y in self.TAIL_STYLE.items() \
                               if y ==options['style']['head']['name'])
            
        if self.head_style == 'harpoon':
            self.harpoon_head_side = next(x for x,y in self.SIDE.items() \
                                          if y == options['style']['head']['side'])
            
        self.color_hue = edge.label_color.h
        self.color_sat = edge.label_color.s
        self.color_lum = edge.label_color.l
        self.color_alph = edge.label_color.a
        
        self.save()
        
            
class Object(StructuredNode, Model):
    #uid = UniqueIdProperty()
    name = StringProperty(max_length=MAX_TEXT_LENGTH, required=True)
    morphisms = RelationshipTo('Object', 'MAPS_TO', model=Morphism)    

    # Position & Color:
    x = IntegerProperty(default=0)
    y = IntegerProperty(default=0) 
    
    color_hue = IntegerProperty(default=0)
    color_sat = IntegerProperty(default=0)
    color_lum = IntegerProperty(default=0)
    color_alph = FloatProperty(default=1.0)       
           
    def copy_relations_from(self, old):
        for f in old.morphisms:
            self.morphisms.connect(f.end_node())   
        self.save()
        
    @staticmethod
    def create_from_editor(vertex):
        o = Object(name=vertex.label.string)
        o.x = vertex.x
        o.y = vertex.y
        o.color_hue = vertex.label_color.h
        o.color_sat = vertex.label_color.s
        o.color_lum = vertex.label_color.l
        o.color_alph = vertex.label_color.a
        o.save()   
        return o
    
    
class Category(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(max_length=MAX_TEXT_LENGTH, required=True)
    objects = RelationshipTo('Object', 'CONTAINS')
    of_categories = BooleanProperty(default=False)
    
    @staticmethod
    def our_create(**kwargs):
        category = Category(**kwargs).save()
        return category
                
    def copy_relations_from(self, old):
        for x in old.objects:
            self.objects.connect(x.end_node())
        self.save()
        
    def delete_objects(self):
        for o in self.objects.all():
            o.delete()
        self.save()
        
    def add_objects(self, obs):
        for o in obs:
            self.objects.connect(o)
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
    
    # Mathematics
    functor = StringProperty()
    # The link to an actual known functor, if this rule is factorial, or None otherwise
    
    # We will have to be careful when deleting a Functor.  We can only delete it
    # if there exist no rules referring to it through this property.
    
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