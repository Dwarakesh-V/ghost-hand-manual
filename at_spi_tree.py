# sudo apt install python3-gi gir1.2-atspi-2.0 at-spi2-core
# python3/python/py -m venv .venv --system-site-packages

# Custom
import pyatspi

# Built-in
import subprocess

def focus_window_by_pid(pid: int) -> None:
    search = subprocess.run(
        ["xdotool", "search", "--pid", str(pid)],
        capture_output=True,
        text=True
    )

    if search.returncode != 0 or not search.stdout.strip():
        return

    for wid in search.stdout.split():
        subprocess.run(
            ["xdotool", "windowactivate", wid],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
    
def get_focused_window_pid():
    try:
        wid = subprocess.check_output(
            ["xdotool", "getwindowfocus"],
            stderr=subprocess.DEVNULL
        ).strip()

        pid = subprocess.check_output(
            ["xdotool", "getwindowpid", wid],
            stderr=subprocess.DEVNULL
        ).strip()

        return int(pid)

    except subprocess.CalledProcessError:
        return None

# Accessibility tree elements
def get_text_content(accessible):
    """Helper to get text from the Text interface if Name is empty"""
    try:
        if accessible.name and accessible.name.strip():
            return accessible.name
            
        # text interface
        text_iface = accessible.queryText()
        content = text_iface.getText(0, -1)
        if content and content.strip():
            return content.strip()
            
    except:
        pass
    return ""

def is_relevant_element(accessible):
    try:
        state = accessible.getState()
        
        # 1. Basic Visibility
        if not (state.contains(pyatspi.STATE_VISIBLE) and state.contains(pyatspi.STATE_SHOWING)):
            return False
        if state.contains(pyatspi.STATE_DEFUNCT):
            return False

        # 2. Check Roles
        role = accessible.getRoleName().lower()
        
        # Note: 'paragraph', 'heading', 'section' are key for your quiz questions
        static_roles = [
            'label', 'static', 'text', 'heading', 'image', 'icon', 
            'paragraph', 'terminal', 'section', 'document', 'panel', 'entry'
        ]
        
        is_static_info = any(sr in role for sr in static_roles)
        is_interactive = ((state.contains(pyatspi.STATE_ENABLED) or
                          state.contains(pyatspi.STATE_FOCUSABLE)) and
                          state.contains(pyatspi.STATE_SENSITIVE))

        # 3. Check for Content (Name OR Text Interface)
        # This is where the previous version failed for <p> tags
        content = get_text_content(accessible)
        has_content = len(content) > 0

        # We keep it if it's interactive OR (it's a static role AND has text)
        return is_interactive or (is_static_info and has_content)
    except:
        return False

def get_element_info(accessible, depth):
    try:
        # Use our new helper to get the real text
        name = get_text_content(accessible)
        role = accessible.getRoleName()
        description = accessible.description or ""
        
        # Relations
        relations_info = []
        try:
            rel_set = accessible.getRelationSet()
            for i in range(rel_set.getNRelations()):
                rel = rel_set.getRelation(i)
                rtype = rel.getRelationType()
                
                if rtype == pyatspi.RELATION_LABELLED_BY:
                    target = rel.getTarget(0)
                    t_name = get_text_content(target) # Use helper here too
                    relations_info.append(f"LabelledBy: '{t_name}'")
                elif rtype == pyatspi.RELATION_LABEL_FOR:
                    target = rel.getTarget(0)
                    t_name = get_text_content(target)
                    relations_info.append(f"LabelFor: '{t_name}'")
        except:
            pass

        component = accessible.queryComponent()
        extents = component.getExtents(0) 
        
        full_description = description
        if relations_info:
            rel_str = " | ".join(relations_info)
            full_description = f"{full_description} ({rel_str})" if full_description else rel_str

        return {
            'name': name, # Can now contain static elements
            'role': role,
            'description': full_description,
            'depth': depth,
            'location': ((extents.x*2)+10, (extents.y*2)+10),
            'width': extents.width,
            'height': extents.height
        }
    except Exception as e:
        return None

def traverse_tree(accessible, depth=0, max_depth=50):
    """Recursively traverse the accessibility tree for both static and interactive elements"""
    if depth > max_depth:
        return []
    
    elements = []
    
    try:
        # Check relevance
        if is_relevant_element(accessible):
            info = get_element_info(accessible, depth)
            if info:
                elements.append(info)
        
        # Traverse children
        for i in range(accessible.childCount):
            try:
                child = accessible.getChildAtIndex(i)
                if child:
                    elements.extend(traverse_tree(child, depth + 1, max_depth))
            except:
                continue
                
    except Exception:
        pass
    
    return elements