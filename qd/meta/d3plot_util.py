from itertools import imap, chain
from pkg_resources import resource_string
import io, json, numpy as np, uuid
from zipfile import ZipFile, ZIP_DEFLATED
from base64 import b64encode

__author__ = 'Dirk Toewe (& Constantin Diez)'

_jszip_js  = '<script type="text/javascript">' + resource_string(__name__, 'jszip.min.js').decode('utf8') + '</script>'
_three_js  = '<script type="text/javascript">' + resource_string(__name__, 'three.min.js').decode('utf8') + '</script>'
_chroma_js = '<script type="text/javascript">' + resource_string(__name__,'chroma.min.js').decode('utf8') + '</script>'
_jquery_js = '<script type="text/javascript">' + resource_string(__name__,'jquery.min.js').decode('utf8') + '</script>'

_d3plot_html_template = resource_string(__name__,'d3plot_html.template').decode('utf8')

def elements_iterator( d3plot, partlist=None ):
  '''
  Returns an iterator of the elements of the parts from a D3Plot whose part id is in the given part list.

  Parameters
  ----------
  d3plot: qd.cae.dyna.D3plot
    The D3Plot whose part's elements are to be iterated.
  partlist: iterable[int]
    A list of part ids whose elements are to be displayed. The order of pids is not relevant.

  Returns
  -------
  elem_iter: iter[qd.cae.dyna.Element]
  '''
  
  # check and handle partlist
  if not partlist:
    partlist = sorted([part.get_id() for part in d3plot.get_parts()])
  else:
    partlist = sorted(set(partlist))
  
  # return iterator
  return chain.from_iterable(
    d3plot.get_partByID(partID).get_elements()
    for partID in partlist
  )


def d3plot_html_div( elements, iTime, text = lambda elem: elem.get_type() + '#' + str(elem.get_id()), intensity = lambda elem,node: 0, lowIntensity=None, highIntensity=None ):
  '''
  Returns an HTML div containing a 3D view of the given parts of a d3plot.

  Parameters
  ----------
  elements: iterable[qd.cae.dyna.Element]
    The elements which are to be displayed.
  iTime: int
    The index of the timestep for which the displacements are plotted in the html view.
  intensity: (qd.cae.dyna.Element,qd.cae.dyna.Node) -> float
    A function which calculates the intensity of a node. The intensity is used together with a color map
	to determine the displayed color.
  text: (qd.cae.dyna.Element) -> float
    A function which returns the text to be displayed for an element. 

  Returns
  -------
  html_div: str
    An HTML <div> as string.
  '''
#   assert 'intensities' not in textThis
#   assert 'positions'   not in textThis

  texts = []

  def tri_data():

    for elem in elements:
  
      if 'shell' == elem.get_type():
  
        nodes = elem.get_nodes()
        nNodes = len({ node.get_id() for node in nodes })
        assert nNodes in {3,4}

        for n in nodes[:3]:
          x,y,z = n.get_coords(iTime)
          yield np.array([x,y,z, intensity(elem,n)], dtype=np.float32 )

        texts.append( text(elem) )

        if 4 == nNodes:

          texts.append(None)

          for n in ( nodes[0], nodes[2], nodes[3] ):
            x,y,z = n.get_coords(iTime)
            yield np.array([x,y,z, intensity(elem,n)], dtype=np.float32 )

  tri_data = np.vstack( tri_data() )
  assert tri_data.dtype == np.float32

  intensities = tri_data[:,3]
  positions   = tri_data[:,:3].flatten()

  if None is  lowIntensity:  lowIntensity = np.min(intensities)
  if None is highIntensity: highIntensity = np.max(intensities)

  assert 1 == intensities.ndim
  assert 1 ==   positions.ndim

  zdata = io.BytesIO()
  with ZipFile(zdata,'w',compression=ZIP_DEFLATED) as zipFile:
    zipFile.writestr('/intensities', intensities.tobytes() )
    zipFile.writestr('/positions',     positions.tobytes() )
    zipFile.writestr('/text', json.dumps(texts) )
  zdata = b64encode( zdata.getvalue() ).decode('utf-8')

  div_id = uuid.uuid4()

  return _d3plot_html_template.format( **locals() )

  

def d3plot_html( elements, iTime, text = lambda elem: elem.get_type() + '#' + str(elem.get_id()), intensity = lambda elem,node: 0, lowIntensity=None, highIntensity=None ):
  '''
  Returns an HTML document containing a 3D view of the given parts of a d3plot.

  Parameters
  ----------
  elements: iterable[qd.cae.dyna.Element]
    The elements which are to be displayed.
  iTime: int
    The index of the timestep for which the displacements are plotted in the html view.
  intensity: (qd.cae.dyna.Element,qd.cae.dyna.Node) -> float
    A function which calculates the intensity of a node. The intensity is used together with a color map
	to determine the displayed color.
  text: (qd.cae.dyna.Element) -> float
    A function which returns the text to be displayed for an element. 

  Returns
  -------
  html: str
    An HTML document as string.
  '''
  html_div = d3plot_html_div(elements, iTime, text, intensity, lowIntensity, highIntensity)
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
    </html>
  '''.format(
    html_div = html_div,
    _jszip_js = _jszip_js,
    _three_js = _three_js,
    _chroma_js=_chroma_js,
    _jquery_js=_jquery_js
  )