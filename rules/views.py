from django.shortcuts import render, redirect, HttpResponse
from database_service.models import (Object, Category, Diagram, get_model_by_uid, get_model_class,
                                     DiagramRule, Morphism)
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.permissions import is_editor
from QuiverDatabase.http_tools import get_posted_text
from django.http import JsonResponse
from QuiverDatabase.python_tools import full_qualname
import json
from django.db import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from QuiverDatabase.settings import DEBUG
from neomodel import db
from QuiverDatabase.variable import Variable
from QuiverDatabase.keyword import Keyword
from QuiverDatabase.neo4j_tools import escape_regex_str

# Create your views here.

@login_required
@user_passes_test(is_editor)
def rule_editor(request, rule_id):
    try:   
        session = request.session
        user = request.user.username
        
        if 'rule ids' not in session:
            session['rule ids'] = []
            
        rule = get_model_by_uid(DiagramRule, uid=rule_id)
        
        if rule.checked_out_by is None:
            if rule.can_be_checked_out():
                rule.checked_out_by = user
                session['rule ids'].append(rule_id)
                session.save()
        else:
            if rule.checked_out_by != user:
                raise OperationalError(
                    f'The rule with id "{rule_id}" is already checked out by {rule.checked_out_by}.')
        
        view_only = request.GET.get('viewonly', 'no')
        
        if view_only != 'no':
            view_only = 'yes'
        
        context = {
            'rule' : rule,
            'key_diagram' : rule.key_diagram.single(),
            'result_diagram' : rule.result_diagram.single(),
            'view_only' : view_only,
        }
        
        return render(request, 'rule_editor.html', context)
        
    except Exception as e:
        return redirect('error', f'{full_qualname(e)}: {str(e)}')
    


@login_required
@user_passes_test(is_editor)
def create_new_rule(request):
    try:          
        rule = DiagramRule.our_create(key='Key', res='Result', name='')
        rule.checked_out_by = request.user.username
        rule.save()
        
        #request.session['new rule id'] = rule.uid  # BUGFIX: cannot pass rule to session itself (not JSON-serializable)
        
        context = {
            'rule' : rule
        }
    
        return render(request, 'new_rule.html', context)
    
    except Exception as e:
        #if DEBUG:
            #raise e
        return redirect('error', f'{full_qualname(e)}: {str(e)}')
    

rule_search_orders = [
    ('creator', 'Creator Name'),
    ('created', 'Date Created'),
    ('edited', 'Date Edited'),
    ('usages', 'Number of Usages'),
    ('views', 'Number of Views'),
    ('votes', 'Sum of Votes'),
    ('name', 'Rule Name'),
]

rule_search_order_map = { param: text for param,text in rule_search_orders }

@login_required
def rule_search(request, diagram_id:str):
    try:        
        # Starting from longest paths first should shorten the final search query (not this one)
        paths_by_length = \
            f"MATCH (D:Diagram)-[:CONTAINS]->(X:Object), " + \
            f"p=(X)-[:MAPS_TO*]->(:Object) " + \
            f"WHERE D.uid = '{diagram_id}' " + \
            f"RETURN p " + \
            f"ORDER BY length(p) DESC" 
        
        paths_by_length, meta = db.cypher_query(paths_by_length)
                
        #results, meta = db.cypher_query(
            #f"MATCH (X:Object) " +
            #f"WHERE X.name =~ '{template_regex}' " +
            #f"RETURN X")  
            
        ## TODO: test code with doublequote in template_regex ^^^
                
        nodes = {
            # Keyed by Object.diagram_index, value is Object
        }
        rels = {
            # Keyed by Morphism.diagram_index, value is Morphism
        }

        node_var = 'n'
        rel_var = 'r'
        search_query = ''
               
        for path in paths_by_length:
            path = path[0]   # [0] is definitely needed here
            node = Object.inflate(path.start_node)
            
            search_query += f"({node_var}{node.diagram_index}:Object)"
            
            if node.diagram_index not in nodes:
                nodes[node.diagram_index] = node
            
            add_query = ''
            
            for rel in path.relationships:
                rel = Morphism.inflate(rel)
                
                if rel.diagram_index not in rels:
                    rels[rel.diagram_index] = rel
                    
                    add_query += f"-[{rel_var}{rel.diagram_index}:MAPS_TO]->"
                    next_node = rel.end_node()  # BUGFIX: no need to inflate here
                    add_query += f"({node_var}{next_node.diagram_index}:Object)"
            
            if add_query:      
                search_query += add_query
                
            search_query += ', '
                        
        rules = []
        
        if search_query:
            search_query = search_query[:-2]   # Remove last ', '
            search_query = "MATCH " + search_query            
            
            regexes = {
                # Keyed by node or relationship .name property, values are neo4j regexes
            }
            
            variables = {
                # Keyed by the actual variable object, values are tuples (Variable, occurences)
                # where occurences is a list of (node or rel, template_index)
            }
            
            def regex_from_template(template):
                regex = ""
                for piece in template:
                    if isinstance(piece, Variable):
                        regex += ".+"
                    elif isinstance(piece, Keyword):
                        regex += escape_regex_str(str(piece))
                    else:  # str
                        regex += escape_regex_str(piece)                
                return regex           
            
            for node in nodes.values():
                name = node.name
                if name not in regexes:
                    template, vars = Variable.parse_into_template(name)
                    regexes[name] = regex_from_template(template)                                 
                    
            for rel in rels.values():
                name = rel.name
                if name not in regexes:
                    template, vars = Variable.parse_into_template(name)
                    regexes[name] = regex_from_template(template)
            
            search_query += " WHERE "
            
            for index, node in nodes.items():
                search_query += f"{node_var}{index}.name =~ '{regexes[node.name]}' AND "
                
            if rels:
                for index, rel in rels.items():
                    search_query += f"{rel_var}{index}.name =~ '{regexes[rel.name]}' AND "
                
            search_query = search_query[:-4]   # Remove AND except a space                
            
            #node_names = [node_name + str(i) for i in range(len(nodes))]
            #rel_names = [rel_name + str(i) for i in range(len(rels))]
            search_query += "RETURN n0"  # We only need n0 to get a diagram id at this stage of the app UX
            
            results, meta = db.cypher_query(search_query)
            
            if results and results[0]:
                n0 = Object.inflate(results[0][0])
                
                diagram, meta = db.cypher_query(
                    f"MATCH (D:Diagram)-[:CONTAINS]->(X:Object) WHERE X.uid = '{n0.uid}' RETURN D")
                
                if diagram and diagram[0]:
                    diagram = Diagram.inflate(diagram[0][0])
                    rules_query = \
                        f"MATCH (R:DiagramRule)-[:KEY_DIAGRAM]->(D:Diagram) " + \
                        f"WHERE D.uid = '{diagram.uid}' RETURN R" 
                    
                    #HERE'S WHERE WE INSERT ORDERING CODE also key / result search^^
                    
                    results, meta = db.cypher_query(rules_query)                
                    
                    for rule in results:
                        rules.append(DiagramRule.inflate(rule[0]))
                
        ascending = request.GET.get('asc', 'true')
        order_param = request.GET.get('ord', 'name')
        
        if order_param not in rule_search_order_map:
            raise ValueError(order_param + " is not a valid value to order by.")
        
        order_text = rule_search_order_map[order_param]
        
        context = {
            'diagram_id' : diagram_id,
            'order_param' : order_param,
            'order_text' : order_text,
            'orders' : rule_search_orders,
            'rules' : rules,
            'ascending' : ascending,
        }
        
        return render(request, 'rule_search.html', context)
        
    except Exception as e:
        if DEBUG:
            raise e
        return redirect('error', f'{full_qualname(e)}: {str(e)}')    
    
    
@login_required
@user_passes_test(is_editor)
def apply_rule(request, rule_id:str, diagram_id:str):
    try:
        rule = get_model_by_uid(DiagramRule, uid=rule_id)
        diagram = get_model_by_uid(Diagram, uid=diagram_id)
        
        var_map = diagram.get_variable_mapping(rule.key_diagram.single())
        
        # Create a new diagram with rule applied and variables appropriately substituted.
       
    except Exception as e:
        #if DEBUG:
            #raise e
        redirect('error', f'{full_qualname(e)}: {str(e)}')
    
    
def rule_viewer(request, rule_id):
    try:   
        session = request.session
        user = request.user.username
 
        rule = get_model_by_uid(DiagramRule, uid=rule_id)
        key_diagram = rule.key_diagram.single()
        res_diagram = rule.result_diagram.single()
        
        context = {
            'rule' : rule,
            'key_diagram' : key_diagram,
            'result_diagram' : res_diagram,
            'view_only' : 'no',
        }
        
        return render(request, 'rule_editor.html', context)
        
    except Exception as e:
        return redirect('error', f'{full_qualname(e)}: {str(e)}')