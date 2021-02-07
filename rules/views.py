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
from collections import OrderedDict

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
        ascending = request.GET.get('asc', 'true')
        order_param = request.GET.get('ord', 'name')
        one_to_one = request.GET.get('onetoone', '1')
        
        if ascending not in ('true', 'false'):
            raise ValueError(f'Invalid order direction parameter (asc) value: {ascending}')
        
        if one_to_one not in ('0', '1'):
            raise ValueError(f'Invalid one-to-one parameter (onetoone) value: {one_to_one}')
        
        if order_param not in rule_search_order_map:
            raise ValueError(order_param + " is not a valid value to order by.")        
        
        # Starting from longest paths first should shorten the final search query (not this one)        
        paths_by_length = Diagram.get_paths_by_length(diagram_id)          
        nodes, rels, search_query = Diagram.build_query_from_paths(paths_by_length)
                        
        rules = []
        
        if search_query:
            regexes, search_query = Diagram.build_match_query(search_query, nodes, rels)
            search_query += "RETURN n0"  # We only need n0 to get a diagram id at this stage of the app UX
            
            results, meta = db.cypher_query(search_query)
            
            rule_memo = {
                # To weed out duplicated results, keyed by rule.uid
            }
            
            for result in results:
                n0 = Object.inflate(result[0])
                
                diagram_results, meta = db.cypher_query(
                    f"MATCH (D:Diagram)-[:CONTAINS]->(X:Object) WHERE X.uid = '{n0.uid}' RETURN D.uid")
                
                if diagram_results and diagram_results[0]:
                    result_diagram_id = diagram_results[0][0]
                    rules_query = \
                        f"MATCH (R:DiagramRule)-[:KEY_DIAGRAM]->(D:Diagram) " + \
                        f"WHERE D.uid = '{result_diagram_id}' RETURN R" 
                    
                    #HERE'S WHERE WE INSERT ORDERING CODE also key / result search^^
                    
                    results, meta = db.cypher_query(rules_query)                
                    
                    for rule in results:
                        rule = DiagramRule.inflate(rule[0])
                        
                        key_diagram = rule.key_diagram.single()
                        if rule.uid not in rule_memo:
                            if one_to_one == '1':
                                if len(key_diagram.objects) != len(nodes) or key_diagram.morphism_count() != len(rels):
                                    continue                        

                            rule_memo[rule.uid] = rule
                            rules.append(rule)                           
        
        order_text = rule_search_order_map[order_param]
        
        context = {
            'diagram_id' : diagram_id,
            'order_param' : order_param,
            'order_text' : order_text,
            'orders' : rule_search_orders,
            'rules' : rules,
            'ascending' : ascending,
            'one_to_one' : one_to_one,
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
        one_to_one = request.GET.get('onetoone', '1')
        
        if one_to_one not in ('0', '1'):
            raise ValueError(f'Invalid one-to-one parameter (onetoone) value: {one_to_one}')
        
        # Starting from longest paths first should shorten the final search query (not this one)        
        paths_by_length = Diagram.get_paths_by_length(diagram_id)      
        print(paths_by_length)
        nodes, rels, search_query = Diagram.build_query_from_paths(paths_by_length)
        
        if search_query:
            search_query += ", (R:DiagramRule)-[:KEY_DIAGRAM]->(D:Diagram)-[:CONTAINS]->(n0)"
            template_regexes, search_query = Diagram.build_match_query(search_query, nodes, rels)
            search_query += f" AND R.uid = '{rule_id}'"
            
            node_vars = OrderedDict([('n' + str(i), nodes[i]) for i in range(len(nodes))])
            rel_vars = OrderedDict([('r' + str(i), rels[i]) for i in range(len(rels))])
            
            search_query += " RETURN " + ','.join(node_vars.keys()) + ',' + ','.join(rel_vars.keys())
                        
            results, meta = db.cypher_query(search_query)
                        
            if results:  # Then rule_id is correct
                results = results[0]  # Holds the unique list of all the various nodes, rels matched
                
                variable_map = {
                    # Keyed by matched Variable objects
                }                   
                
                def populate_variable_map(Model, model_vars, results):
                    if Model == Object:
                        var_name = 'n'
                    elif Model == Morphism:
                        var_name = 'r'
                        
                    for i in range(len(results)):
                        query_node = model_vars[var_name + str(i)]
                        
                        matched_node = Model.inflate(results[i])
                        matched_template, matched_vars = Variable.parse_into_template(matched_node.name)
                        
                        query_template = template_regexes[query_node.name][0]
                        
                        var_subst_regex, var_count = Variable.variable_match_regex(query_template)
                        match = var_subst_regex.match(query_node.name)    # BUGFIX: query_node here not matched_node

                        for i in range(var_count):
                            Vi = match.group('V' + str(i))
                            # Variables need to be matched consistently and we have to check this in both
                            # the apply_rule and rule_search since the user can pass in an ultimately inconsistent
                            # yet skeletally matched query diagram.                        
                            matched_var = matched_vars[i]
                            
                            if matched_var in variable_map:
                                if variable_map[matched_var] != Vi:
                                    raise OperationalError("The diagram variables are not matched consitently.")
                            else:
                                variable_map[matched_var] = Vi

                rule = get_model_by_uid(DiagramRule, uid=rule_id)
                
                if one_to_one == '1':
                    key_diagram = rule.key_diagram.single()
                    
                    if len(key_diagram.objects) != len(nodes) or key_diagram.morphism_count() != len(rels):
                        raise OperationalError(
                            "There is no one-to-one correspondence of the diagram's objects/morphisms with those of the rule.")
                
                output_diagram = rule.result_diagram.single()    
                                                    
                populate_variable_map(Object, node_vars, results[:len(node_vars)])
                populate_variable_map(Morphism, rel_vars, results[len(node_vars):])
                
                output_names = {
                    # Keyed by name, value is flattened template of that that name, after variable subst
                }                               
                
                # Create the new diagram
                new_diagram = output_diagram.copy(name=rule.name, checked_out_by=request.user.username)                
                
                for X in new_diagram.all_objects():
                    if X.name not in output_names:
                        output_template, vars = Variable.parse_into_template(X.name)
                        Variable.subst_vars_into_template(output_template, variable_map)
                        output_names[X.name] = Variable.flatten_template(output_template)
                    X.name = output_names[X.name]
                    X.save()
                    
                    for f in X.all_morphisms():
                        if f.name not in output_names:
                            output_template, vars = Variable.parse_into_template(f.name)
                            Variable.subst_vars_into_template(output_template, variable_map)
                            output_names[f.name] = Variable.flatten_template(output_template)
                        f.name = output_names[f.name]
                        f.save()
                
                #new_diagram.save()
                return redirect('diagram_editor', new_diagram.uid)
            
        redirect('error', 'That rule cannot be applied to this diagram.')
        
    except Exception as e:
        if DEBUG:
            raise e
        return redirect('error', f'{full_qualname(e)}: {str(e)}')
    
    
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