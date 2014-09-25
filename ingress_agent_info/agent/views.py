from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response

from agent.models import Agent, PlayArea

def get_profile_context(user_id):
    if user_id is None:
        return {}
    try:
        agent = Agent.objects.get(user__id=user_id)
        return {'agent':agent, 'profile':agent.user.profile, 'user':agent.user}
    except Agent.DoesNotExist:
        return {}
    
def render_template(template_name, req, cdict=None):
    if cdict is None:
        cdict = {}
    cdict['my_info'] = get_profile_context(req.user.id)
    return render_to_response(template_name, 
                              cdict, 
                              context_instance=RequestContext(req))


@login_required
def agent_info_form(req, **kwargs):
    if req.method == 'GET':
        user_id = kwargs.get('user_id')
        if user_id is None:
            user_id = req.user.id
        cdict = {}
        cdict['agent'] = get_profile_context(user_id)
        cdict['agent_level_range'] = range(1, 17)
        return render_template('agent/info_form.html', req, cdict)
    elif req.method == 'POST':
        pass
    
@login_required
def agent_list(req, **kwargs):
    q = Agent.objects.all()
    cdict = {'agents':q}
    return render_template('agent/list.html', req, cdict)
    
    
