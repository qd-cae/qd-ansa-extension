
import os
import io
import json
import uuid
import numpy as np
from base64 import b64encode
from zipfile import ZipFile, ZIP_DEFLATED

import meta 
from meta import constants
from meta import windows
from meta import models
from meta import results
from meta import nodes
from meta import elements

__authors__ = "D. Toewe & C. Diez"

def read_neighbor_file(filename):
    ''' This function reads a neighboring file as str
    
    Parameters
    ----------
    filename : str
        Filename of file next to this file, which shall be read
        
    Returns
    -------
    file_content : str
    '''
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open( os.path.join(dir_path, filename), "r") as fp:
        return fp.read()
        

def _build_model_html_div(use_fringe=True, fringe_bounds=[None,None] ):
    '''Builds a HTML div from the current model
    
    Parameters
    ----------
    use_fringe : bool
        whether to use fringe in the HTML. True by default.
    fringe_bounds : tuple(float,float)
        fringe bar bounds in the HTML (can not be determined from META fringe bar)
        
    Returns
    -------
    html_div : str
        The active model embedded into an html div
        
    This function returns a string for a HTML div, which contains the active model.
    '''
    
    active_window = windows.ActiveWindow()
    model_list = models.ModelsIn3DWindow(active_window.name)
    
    node_data = []
    element_texts = []
    
    # iterate through all active models
    for current_model in model_list:
        
        # collect visible elements
        elems = elements.VisibleElementsByType(current_model.id, constants.SHELL, active_window.name)
            
        # get active resultset
        active_results = results.CurrentResultset(current_model.id)
        
        # loop through visible elements and write them
        for elem in elems:
            
            # element result data
            elem_results = elements.CentroidScalarOfElement(active_results, elem.type, elem.id, -1)
            if elem_results and use_fringe:
                elem_value = elem_results.value
                element_texts.append("e#%d=%.5f" % (elem.id, elem_value))
            else:
                elem_value = 0.
                element_texts.append("e#%d" % elem.id)
                
            # write nodal data
            elem_nodes = nodes.NodesOfElement(current_model.id, elem.type, elem.id, -1)
            
            for node in elem_nodes[:3]:
                node_coords = nodes.CoordinatesOfNode(active_results, node.id)
                node_data.append( (node_coords.x, node_coords.y, node_coords.z, elem_value) )
            
            # a quad4 is written as second triangle
            if elem.type == constants.QUAD4:
            
                element_texts.append(None)
                
                for node in ( elem_nodes[0], elem_nodes[2], elem_nodes[3] ):
                    node_coords = nodes.CoordinatesOfNode(active_results, node.id)
                    node_data.append( (node_coords.x, node_coords.y, node_coords.z, elem_value) ) 
    
    # convert to numpy and dissemble
    node_data = np.asarray(node_data, dtype=np.float32)
    node_coords = node_data[:,:3].flatten()
    node_fringe = node_data[:,3]
    
    # fringe levels
    fringe_bounds= list(fringe_bounds) # convert in case of tuple (no assignments)
    fringe_bounds[0] = np.amin(node_fringe) if fringe_bounds[0] == None else fringe_bounds[0]
    fringe_bounds[1] = np.amax(node_fringe) if fringe_bounds[1] == None else fringe_bounds[1]
    
    # zip compression of data for HTML (reduces size)
    zdata = io.BytesIO()
    with ZipFile(zdata,'w',compression=ZIP_DEFLATED) as zipFile:
        zipFile.writestr('/intensities', node_fringe.tostring() )
        zipFile.writestr('/positions',   node_coords.tostring() )
        zipFile.writestr('/text', json.dumps(element_texts) )
    zdata = b64encode( zdata.getvalue() ).decode('utf-8')
    
    # read html template
    _html_template = read_neighbor_file("html.template")
    
    # format html template file
    return _html_template.format(div_id       = uuid.uuid4(),
                                 positions    = node_coords, 
                                 intensities  = node_fringe,
                                 lowIntensity = fringe_bounds[0],
                                 highIntensity= fringe_bounds[1],
                                 zdata        = zdata)

                          
def _build_model_html( use_fringe=True, fringe_bounds=[None,None] ):
    ''' Build the whole HTML page for the active model
    
    Parameters
    ----------
    use_fringe : bool
        whether to use fringe in the HTML. True by default.
    fringe_bounds : tuple(float,float)
        fringe bar bounds in the HTML (can not be determined from META fringe bar)
        
    Returns
    -------
    html_page : str
        The active model embedded into an html page
    '''
    _html_div = _build_model_html_div( use_fringe=use_fringe, fringe_bounds=fringe_bounds)
    
    _html_jszip_js = '<script type="text/javascript">%s</script>' % read_neighbor_file('jszip.min.js')  
                     
    _html_three_js = '<script type="text/javascript">%s</script>' % read_neighbor_file('three.min.js')  
                     
    _html_chroma_js = '<script type="text/javascript">%s</script>' % read_neighbor_file('chroma.min.js')  
                       
    _html_jquery_js = '<script type="text/javascript">%s</script>' % read_neighbor_file('jquery.min.js')  
    
    return   '''
<!DOCTYPE html>
<html lang="en">
    <head>
    <meta charset="utf-8" />
        {_jquery_js}
        {_jszip_js}
        {_three_js}
        {_chroma_js}
    </head>
    <body>
        {html_div}
    </body>
</html>'''.format(
    html_div = _html_div,
    _jszip_js = _html_jszip_js,
    _three_js = _html_three_js,
    _chroma_js= _html_chroma_js,
    _jquery_js= _html_jquery_js)
    

def export_to_html(html_filepath, use_fringe=True, fringe_bounds=[None,None] ):
    '''Export the active visible view to a 3D HTML file.
    
    Parameters
    ----------
    html_filepath : str
        Filepath for the exported HTML
    use_fringe : bool
        whether to use fringe in the HTML. True by default.
    fringe_bounds : tuple(float,float)
        fringe bar bounds in the HTML (can not be determined from META fringe bar)
    
    This function exports the active visible view to a 3D HTML file. The fringe
    settings have to be set by hand, since they can not be read from META.
    '''
    _model_html_div = _build_model_html(use_fringe=use_fringe, fringe_bounds=fringe_bounds )
    with open(html_filepath, "w") as fp:
        fp.write(_model_html_div)
        
    
    