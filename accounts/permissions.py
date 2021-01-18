

def is_editor(user):
    return user.groups.filter(name='Editors').exists()