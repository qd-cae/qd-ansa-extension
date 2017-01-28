from d3plot_util import d3plot_html, elements_iterator
from qd.cae.dyna import D3plot
import os, webbrowser

__author__ = 'Dirk Toewe'

def main():
  # the LS Dyna D3Plot file to be read (if femzippe use_femzip=True)
  inputfile = 'G:/Programming/Python/qd/test/d3plot.fz'

  print('Loading D3Plot...')
  d3plot = D3plot( inputfile, use_femzip=True, read_states = ['plastic_strain max', 'disp'] )
  print('Creating HTML View...')

  # the html file to be created
  output = 'd3plot_view.html'

  # the list of part ids which are displayed ONLY SHELLS ARE CURRENTLY DISPLAYED
  partlist = [13,14,15,18,19]

  # the quantity to be displayed as for the nodes (default is plastic strain)
  def intensity( elem, node ):
    strains = elem.get_plastic_strain()
    return strains[-1]# - strains[1]

  # the text to be displayed for an element when mouse hovering over it
  def text( elem ):
    return '{}#{}\n\np. strain (max): {:.6f}'.format( elem.get_type(), elem.get_id(), intensity(elem,None) )

  html = d3plot_html(
    elements_iterator(d3plot,partlist),
	iTime=-1,
	intensity=intensity,
	text=text,
	lowIntensity=0.003,
	highIntensity=0.03
  )

  with open(output,'w') as out:
    out.write(html)
    print('DONE.')
    webbrowser.open('file://'+ os.path.abspath(output) )

if '__main__' == __name__:
  main()