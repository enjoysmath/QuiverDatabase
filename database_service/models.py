from neomodel import *
from django_neomodel import DjangoNode
from django.db import models
from QuiverDatabase.settings import MAX_TEXT_LENGTH
from django.core.exceptions import ObjectDoesNotExist
from neomodel import db
from QuiverDatabase.python_tools import deep_get, deep_set
from QuiverDatabase.variable import Variable

# Create your models here.

class Model:
    @staticmethod
    def our_create(**kwargs):
        raise NotImplementedError
    
    
class Morphism(StructuredRel):
    #uid = StringProperty(default=Morphism.get_unique_id())
    name = StringProperty(max_length=MAX_TEXT_LENGTH)
    
    # RE-DESIGN: TODO - these need to be independent of style and settable in an accompanying
    # panel to the editor.
    # These are the mathematical properties, that you can search by:
    #epic = BooleanProperty(default=False)
    #monic = BooleanProperty(default=False)
    #inclusion = BooleanProperty(default=False)
    
    # Strictly style below this line:   
    NUM_LINES = { 1: 'one', 2: 'two', 3: 'three' }
    num_lines = IntegerProperty(choices=NUM_LINES, default=1)

    LeftAlign, CenterAlign, RightAlign, OverAlign = range(4)
    DefaultAlignment = LeftAlign    
     
    ALIGNMENT = { 0:LeftAlign,  1:RightAlign, 2:CenterAlign, 3:OverAlign}
    alignment = IntegerProperty(choices=ALIGNMENT, default=DefaultAlignment)
    
    label_position = IntegerProperty(default=50)
    offset = IntegerProperty(default=0)
    curve = IntegerProperty(default=0)
    tail_shorten = IntegerProperty(default=0)
    head_shorten = IntegerProperty(default=0)
    
    TAIL_STYLE = {0:'none', 1:'mono', 2:'hook', 3:'arrowhead', 4:'maps_to'}
    tail_style = IntegerProperty(choices=TAIL_STYLE, default=0)
        
    SIDE = {0:'none', 1:'top', 2:'bottom'}
    hook_tail_side = IntegerProperty(choices=SIDE, default=0)    
    
    HEAD_STYLE = {0:'none', 1:'arrowhead', 2:'epi', 3:'harpoon'}
    head_style = IntegerProperty(choices=HEAD_STYLE, default=1)
    harpoon_head_side = IntegerProperty(choices=SIDE, default=0)
    
    BODY_STYLE = {0:'solid', 1:'none', 2:'dashed', 3:'dotted', 4:'squiggly', 5:'barred'}
    body_style = IntegerProperty(choices=BODY_STYLE, default=0)
    
    color_hue = IntegerProperty(default=0)
    color_sat = IntegerProperty(default=0)   # BUGFIX: default (black) is 0,0,0 in hsl, not 0,100,0
    color_lum = IntegerProperty(default=0)
    color_alph = FloatProperty(default=1.0)
    
    def load_from_editor(self, format):  
        if len(format) > 2:
            self.name = format[2]
        
        if len(format) > 3:
            self.alignment = format[3]
        
        if len(format) > 4:                
            options = format[4]            
            self.label_position = options.get('label_position', 50)
            self.offset = options.get('offset', 0)
            self.curve = options.get('curve', 0)
            shorten = options.get('shorten', {'source': 0, 'target': 0})
            self.tail_shorten = shorten.get('source', 0)
            self.head_shorten = shorten.get('target', 0)
            self.num_lines = options.get('level', 1)
            
            self.body_style = next(x for x,y in self.BODY_STYLE.items() \
                                   if y == deep_get(options, ('style', 'body', 'name'), 'solid'))
            
            self.tail_style = next(x for x,y in self.TAIL_STYLE.items() \
                                   if y == deep_get(options, ('style', 'tail', 'name'), 'none' ))
            
            side = deep_get(options, ('style', 'tail', 'side'), 'none')
            
            if isinstance(side, int):
                self.hook_tail_side = side
            else:
                self.hook_tail_side = next(x for x,y in self.SIDE.items() if y == side)
            
            self.head_style = next(x for x,y in self.HEAD_STYLE.items() \
                                   if y == deep_get(options, ('style', 'head', 'name'), 'arrowhead'))
            
            side = deep_get(options, ('style', 'head', 'side'), 'none')
            
            if isinstance(side, int):
                self.harpoon_head_side = side
            else:
                self.harpoon_head_side = next(x for x,y in self.SIDE.items() if y == side)
                
            if len(format) > 5:
                color = format[5]
            elif 'colour' in options:
                color = options['colour']
            else:
                color = [0, 0, 0, 1.0]  # BUGFIX: black is hsl:  0,0,0 not 0,100,0
                
            self.color_hue = color[0]
            self.color_sat = color[1]
            self.color_lum = color[2]
            
            if len(color) > 3:
                self.color_alph = color[3]            
        
        self.save()
        
    def quiver_format(self):
        format = [self.start_node().quiver_index, self.end_node().quiver_index]
        format.append(self.name if self.name is not None else '')
        format.append(self.alignment)
        options = {
            #'colour' : [self.color_hue, self.color_sat, self.color_lum, self.color_alph],
            'label_position': self.label_position,
            'offset' : self.offset,
            'curve' : self.curve,
            'shorten' : {
                'source' : self.tail_shorten,
                'target' : self.head_shorten,
            },
            'level' : self.num_lines,
            'style' : {
                'tail': {
                    'name' : self.TAIL_STYLE[self.tail_style],
                    'side' : self.SIDE[self.hook_tail_side],
                },
                'head': {
                    'name' : self.HEAD_STYLE[self.head_style],
                    'side' : self.SIDE[self.harpoon_head_side],
                },
                'body': {
                    'name' : self.BODY_STYLE[self.body_style],
                }                    
            },
            'colour' : [self.color_hue, self.color_sat, self.color_lum, self.color_alph],
        }
        format.append(options)
        format.append([self.color_hue, self.color_sat, self.color_lum, self.color_alph])
        return format
    
            
class Object(StructuredNode, Model):
    uid = UniqueIdProperty()
    name = StringProperty(max_length=MAX_TEXT_LENGTH)
    morphisms = RelationshipTo('Object', 'MAPS_TO', model=Morphism)    
    
    quiver_index = IntegerProperty()

    # Position & Color:
    x = IntegerProperty(default=0)
    y = IntegerProperty(default=0) 
    
    color_hue = IntegerProperty(default=0)
    color_sat = IntegerProperty(default=0)
    color_lum = IntegerProperty(default=0)
    color_alph = FloatProperty(default=1.0) 
    
    def __repr__(self):
        return f'Object("{self.name}")'
    
    def all_morphisms(self):
        results, meta = db.cypher_query(
            f'MATCH (x:Object)-[f:MAPS_TO]->(y:Object) WHERE x.uid="{self.uid}" RETURN f')
        return [Morphism.inflate(row[0]) for row in results]
                    
    def delete(self):
        # Delete all the outgoing morphisms first:
        db.cypher_query(f'MATCH (o:Object)-[f:MAPS_TO]-(p:Object) WHERE o.uid="{self.uid}" DELETE f')       
        super().delete()
           
    @staticmethod
    def create_from_editor(format, index:int):
        o = Object()
        o.init_from_editor(format, index)
        return o
        
    def init_from_editor(self, format, index):
        o = self
        
        o.quiver_index = index
        o.x = format[0]
        o.y = format[1]
        
        if len(format) > 2:
            o.name = format[2]
            
        if len(format) > 3:
            color = format[3]
            o.color_hue = color[0]
            o.color_sat = color[1]
            o.color_lum = color[2]
            o.color_alph = color[3]
        
        o.save()   
        return o
    
    def quiver_format(self):
        return [self.x, self.y, self.name, 
                [self.color_hue, self.color_sat, self.color_lum, self.color_alph]]
   
        
        
class Category(StructuredNode, Model):
    unique_fields = ['name']
    uid = UniqueIdProperty()
    name = StringProperty(max_length=MAX_TEXT_LENGTH, required=True)
    objects = RelationshipTo('Object', 'CONTAINS')
    of_categories = BooleanProperty(default=False)

    @staticmethod
    def our_create(**kwargs):
        category = Category(**kwargs).save()
        return category
    
        
class Diagram(StructuredNode, Model):  
    """
    Models should be decouple (inheritance rarely used)
    Otherwise basic seeming queries return all types in the hierarchy.
    Hence just StructuredNode here.
    """
    uid = UniqueIdProperty()
    name = StringProperty(max_length=MAX_TEXT_LENGTH, required=True)
    objects = RelationshipTo('Object', 'CONTAINS')    
    category = RelationshipTo('Category', 'IN_CATEGORY', cardinality=One)
    COMMUTES = { 'C' : 'Commutes', 'NC' : 'Noncommutative' }
    commutes = StringProperty(choices=COMMUTES, default='C')
    checked_out_by = StringProperty(max_length=MAX_TEXT_LENGTH)
    
    @property
    def commutes_text(self):
        return self.COMMUTES[self.commutes]
    
    #@property
    #def commutes(self):
        #return self.COMMUTES[self.commutative]
    
    #@commutes.setter
    #def commutes(self, text):
        #for key, val in self.COMMUTES.items():
            #if text == val:
                #self.commutative = key
                #break
        #else:
            #raise ValueError(f'There are only {len(self.COMMUTES)} possible options for Diagram.commutes')
    
    @staticmethod
    def our_create(**kwargs):
        diagram = Diagram(**kwargs).save()
        category = get_unique(Category, name='Any')
        diagram.category.connect(category)
        diagram.save()  
        return diagram
        
    def quiver_format(self):
        edges = []
        vertices = []
        
        objects = list(self.all_objects())
        objects.sort(key=lambda x: x.quiver_index)        
        
        for o in objects:
            vertices.append(o.quiver_format())
            for f in o.all_morphisms():
                edges.append(f.quiver_format())
                    
        format = [0, len(vertices)]
        format += vertices
        format += edges
        
        return format
    
    def load_from_editor(self, format):
        obs = []
        vertices = format[2:2 + format[1]]
        
        for k,v in enumerate(vertices):
            o = Object.create_from_editor(v, k)
            obs.append(o)
        
        edges = format[2 + format[1]:]
            
        for e in edges:
            A = obs[e[0]]
            B = obs[e[1]]
            f = A.morphisms.connect(B)
            f.load_from_editor(e)
            f.save()
            A.save()            
            
        self.add_objects(obs)               
    
    def all_objects(self):
        results, meta = db.cypher_query(
            f'MATCH (D:Diagram)-[:CONTAINS]->(x:Object) WHERE D.uid="{self.uid}" RETURN x')
        return [Object.inflate(row[0]) for row in results]
        
    def delete_objects(self):
        for o in self.all_objects():
            o.delete()
        self.save()
        
    def add_objects(self, obs):
        for o in obs:
            self.objects.connect(o)
        self.save()


class NaturalMap(Morphism):
    pass


class FunctorOb(Object):
    def all_morphisms(self):
        results, meta = db.cypher_query(
            f'MATCH (x:NaturalMap)-[f:MAPS_TO]->(y:NaturalMap) WHERE x.uid="{self.uid}" RETURN f')
        return [NaturalMap.inflate(row[0]) for row in results]
                    
    def delete(self):
        # Delete all the outgoing morphisms first:
        db.cypher_query(f'MATCH (o:FunctorOb)-[f:MAPS_TO]-(p:FunctorOb) WHERE o.uid="{self.uid}" DELETE f')       
        super().delete()
           
    @staticmethod
    def create_from_editor(format, index:int):
        o = FunctorOb()
        Object.init_from_editor(self, format, index)
        
        

class DiagramRule(StructuredNode, Model):
    uid = UniqueIdProperty()
    name = StringProperty(max_length=MAX_TEXT_LENGTH, required=True)
    checkedOutBy = StringProperty(max_length=MAX_TEXT_LENGTH)
    key_diagram = RelationshipTo('Diagram', 'KEY_DIAGRAM', cardinality=One)
    result_diagram = RelationshipTo('Diagram', 'RESULT_DIAGRAM', cardinality=One)
    
    # Mathematics
    #functor_id = StringProperty()
    # The link to an actual known functor, if this rule is factorial, or None otherwise
    # We will have to be careful when deleting a Functor.  We can only delete it
    # if there exist no rules referring to it through this property.
    
    @property
    def checked_out_by(self):
        return self.checkedOutBy
    
    @checked_out_by.setter
    def checked_out_by(self, username):
        if self.checked_out_by != username:
            diagram = self.key_diagram.single()
            diagram.checked_out_by = username
            diagram.save()
            diagram = self.result_diagram.single()
            diagram.checked_out_by = username
            diagram.save()
            self.checkedOutBy = username
            self.save()
            
    def can_be_checked_out(self):
        return self.key_diagram.single().checked_out_by is None and \
            self.result_diagram.single().checked_out_by is None and \
            self.checked_out_by is None
    
    @staticmethod
    def our_create(key=None, res=None, **kwargs):
        if key is None:
            key = 'Key'
        if res is None:
            res = 'Result'
            
        cat = get_unique(Category, name='Any')    
        source = Diagram(name=key).save()
        source.category.connect(cat)
        source.save()
        target = Diagram(name=res).save()
        target.category.connect(cat)
        target.save()
        rule = DiagramRule(**kwargs)
        rule.save()
        rule.key_diagram.connect(source)
        rule.result_diagram.connect(target)
        rule.save()
        return rule
        
    #@staticmethod
    #def get_variable_mapping(source:Diagram, target:Diagram) -> dict:
        #map = {}
        
        #for x in source.all_objects():
            #template, vars = Variable.parse_template(text)
                
    #def get_variable_template_regex(self, text:str) -> bidict:       

model_str_to_class = {
    'Category' : Category,
    'Object' : Object,
    'Diagram' : Diagram,
    'DiagramRule' : DiagramRule,
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
        model = Model.our_create(**kwargs)
        model.save()
        
    return model