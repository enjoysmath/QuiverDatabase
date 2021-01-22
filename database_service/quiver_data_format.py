#The format we use for encoding quivers in base64 (primarily for link-sharing) is
#the following. This has been chosen based on minimality (for shorter representations),
#rather than readability.

#Note that an empty quiver has no representation.

#`[version: integer, |vertices|: integer, ...vertices, ...edges]`

#Parameters:
#- `version` is currently only permitted to be 0. The format has been designed to be
    #forwards-compatible with changes, so it is intended that this version will not
    #change.
#- `|vertices|` is the length of the array `vertices`.
#- `vertices` is an array of vertices of the form:
    #`[x: integer, y: integer, label: string, label_colour: [h, s, l, a]]`
    #+ `label` is optional (if not present, it will default to `""`), though it must be
        #present if any later option is.
    #+ `label_colour` is optional (if not present, it will default to `[0, 0, 0, 1]`).
        #+ `h` is an integer from `0` to `360`
        #+ `s` is an integer from `0` to `100`
        #+ `l` is an integer from `0` to `100`
        #+ `a` is a floating-point number from `0` to `1`
#- `edges` is an array of edges of the form:
    #`[source: index, target: index, label: string, alignment, options, label_colour]`
    #+ (label) `alignment` is an enum comprising the following options:
        #* `0`: left
        #* `1`: centre
        #* `2`: right
        #* `3`: over
        #It has been distinguished from the other options as one that is frequently
        #changed from the default, to avoid the overhead of encoding an options
        #object.
    #+ `options` is an object containing the delta of the options from the defaults.
        #This is the only parameter that is not encoded simply as an array, as the
        #most likely parameter to be changed in the future.
    #+ `label_colour` is stored in the same manner as for vertices.
    
#Example:
# [0,3,[0,1,"\\bullet"],[1,0,"\\bullet"],[1,1,"\\bullet"],[0,2],[2,1],[0,1,"",1,{"label_position":30,"offset":-2,"curve":-3,"shorten":{"source":20},"level":2,"style":{"tail":{"name":"hook","side":"top"}}}]]

#Notes:
#- An `index` is an integer indexing into the array `[...vertices, ...edges]`.
#- Arrays may be truncated if the values of the elements are the default values.

from copy import deepcopy
from QuiverDatabase.python_tools import deep_get, deep_set
import pprint


class QuiverLabel:  
    def __init__(self, string):
        self.string = string
        
    def __deepcopy__(self, memo):
        return QuiverLabel(str(self.string))
    
    def __str__(self):
        return self.string

QuiverLabel.Default = QuiverLabel('')
        

class QuiverColor:   
    def __init__(self, json):
        self.h = json[0]   
        assert(isinstance(self.h, int) and 0 <= self.h <= 360)
        self.s = json[1]
        assert(isinstance(self.s, int) and 0 <= self.s <= 100)
        self.l = json[2]
        assert(isinstance(self.l, int) and 0 <= self.l <= 100)
        self.a = json[3]
        if isinstance(self.a, int):
            self.a = float(self.a)
        assert(isinstance(self.a, float) and 0.0 <= self.a <= 1.0)
                        
    def __deepcopy__(self, memo):
        return QuiverColor([self.h, self.s, self.l, self.a])
    
    def __str__(self):
        return f'[h:{self.h}, s:{self.s}, l:{self.l}, a:{self.a}]'

QuiverColor.Default = QuiverColor([0, 0, 0, 1.0])  


class QuiverVertex:
    def __init__(self, json):
        self.x = json[0]
        self.y = json[1]
        if len(json) > 2:
            self.label = QuiverLabel(json[2])
            if len(json) > 3:
                self.label_color = QuiverColor(json[3])
            else:
                self.label_color = deepcopy(QuiverColor.Default)
        else:
            self.label = deepcopy(QuiverLabel.Default)
            self.label_color = deepcopy(QuiverColor.Default)
            
        
    def __deepcopy__(self, memo):
        return QuiverVertex([self.x, self.y, deepcopy(self.label), deepcopy(self.label_color)])
    
    def __str__(self):
        return f'[x:{self.x}, y:{self.y}\n ' + \
               f'label:{str(self.label)}\n' + \
               f'color:{str(self.label_color)}]'


class QuiverEdge:
    LeftAlign, CenterAlign, RightAlign, OverAlign = range(4)
    DefaultAlignment = LeftAlign
    
    def __init__(self, json):
        self.source_index = json[0]
        self.target_index = json[1]
        if len(json) > 2:
            self.label = QuiverLabel(json[2])
            if len(json) > 3:
                self.alignment = json[3]
                assert(0 <= json[3] <= self.OverAlign)
                
                if len(json) > 4:
                    self.options = QuiverEdgeOptions(json[4])
                    
                    if len(json) > 5:
                        self.label_color = QuiverColor(json[5])
                    else:
                        self.label_color = deepcopy(QuiverColor.Default)
                else:
                    self.options = deepcopy(QuiverEdgeOptions.Default)
                    self.label_color = deepcopy(QuiverColor.Default)
            else:
                self.alignment = self.DefaultAlignment
                self.options = deepcopy(QuiverEdgeOptions.Default)
                self.label_color = deepcopy(QuiverColor.Default)                
        else:
            self.label = deepcopy(QuiverLabel.Default)
            self.alignment = self.DefaultAlignment
            self.options = deepcopy(QuiverEdgeOptions.Default)
            self.label_color = deepcopy(QuiverColor.Default)            
            
    def __deepcopy__(self, memo):
        return QuiverEdge([self.source_index, self.target_index, deepcopy(self.label), 
                           self.alignment, deepcopy(self.options), deepcopy(self.label_color)])
        
    def __str__(self):
        return f'[source:{self.source_index}\n' + \
               f'target:{self.target_index}\n' + \
               f'label:{str(self.label)}\n' + \
               f'alignment:{self.alignment}\n' + \
               f'options:{str(self.options)}\n' + \
               f'color:{str(self.label_color)}]'
                    
                    
class QuiverEdgeOptions:
    TailStyleNames = set(['mono', 'none', 'hook', 'arrowhead', 'maps to'])
    HookTailSides = set(['top', 'bottom'])
    
    BodyStyleNames = set(['none', 'solid', 'dashed', 'dotted', 'squiggly', 'barred'])
    
    HeadStyleNames = set(['arrowhead', 'none', 'epi', 'harpoon'])
    HarpoonHeadSides = set(['top', 'bottom'])
    
    
    def __init__(self, json, init=True):
        if not init:
            return 
        if hasattr(self, 'Default'):
            self.dict = deepcopy(self.Default)
        else:
            self.dict = {}
        
        if 'label_position' in json:
            x = self.dict['label_position'] = json['label_position']
            assert(isinstance(x, int) and 0 <= x <= 100)
                
        if 'offset' in json:
            x = self.dict['offset'] = json['offset']
            assert(isinstance(x, int) and -5 <= x <= 5)
            
        if 'curve' in json:
            x = self.dict['curve'] = json['curve']
            assert(isinstance(x, int) and -5 <= x <= 5)
        
        if 'level' in json:
            x = self.dict['level'] = json['level']
            assert(1 <= x <= 3)
            
        keys = ('style', 'body', 'name')            
        style = deep_set(self.dict, keys, deep_get(json, keys, 'solid'))
        
        assert(style in self.BodyStyleNames)
        
        keys = ('style', 'head', 'name')
        style = deep_set(self.dict, keys, deep_get(json, keys, 'arrowhead'))
        
        assert(style in self.HeadStyleNames)
        
        if style == 'harpoon':
            keys = keys[:-1] + ('side',)
            style = deep_set(self.dict, keys, deep_get(json, keys, 'top'))
            assert (style in self.HarpoonHeadSides)
            
        keys = ('style', 'tail', 'name')
        style = deep_set(self.dict, keys, deep_get(json, keys, 'none'))
        
        assert(style in self.TailStyleNames)
        
        if style == 'hook':
            keys = keys[:-1] + ('side',)
            style = deep_set(self.dict, keys, deep_get(json, keys, 'top'))
            assert(style in self.HookTailSides)
                
                            
    def __deepcopy__(self, memo):
        o = QuiverEdgeOptions({}, init=False)
        o.dict = deepcopy(self.dict)
    
    def __str__(self):
        return pprint.pformat(self.dict)

QuiverEdgeOptions.Default = QuiverEdgeOptions({
    'label_position': 50,
    'offset' : 0,
    'curve' : 0,
    'length_shorten' : {
        'source' : 0,
        'target' : 0,
    },
    'level' : 1,
    'style' : {
        'tail' : {
            'name' : 'none',
        },
        'body' : {
            'name' : 'solid',
        },
        'head' : {
            'name' : 'arrowhead',
        }
    }
})

            
            
class QuiverDataFormat:
    def __init__(self, json):
        self.version = json[0]
        self.number_of_vertices = json[1]
        
        if json[1] != 0:
            self.vertices = [QuiverVertex(v) for v in json[2:2 + json[1]]]
        
            if len(json) > 2 + json[1]:
                self.edges = [QuiverEdge(e) for e in json[2 + json[1]:]]
            else:
                self.edges = []
        else:
            self.vertices = []
            self.edges = []
    
    def __str__(self):
        r = f'version:{self.version}\n' + \
            f'num. verts:{self.number_of_vertices}\n' + \
            f'vertices:[\n'
        
        for v in self.vertices:
            r += str(v) + '\n'
        
        r = r[:-1]
        r += ']\n'
        
        r += 'edges:[\n'
        for e in self.edges:
            r += str(e) + '\n'
        
        r = r[:-1]
        r += ']'
            
        return r
    
    def __repr__(self):
        return str(self)
                
                
QuiverDataFormat.Default = QuiverDataFormat([0, 0])
        
            
        
        