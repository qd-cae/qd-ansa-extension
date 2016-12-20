
# qd-ansa 

This library is a python utility library ANSA from Beta CAE Systems SA. 
This project is not affiliated in any way with the official software. 

# Installation

Just copy the fles into your installation folder: /Path/to/BETA_CAE_Systems/shared_v17.0.2/python/win64/Lib/site-packages

# Classes

The following classes are implemented for usage:

## QDEntity

Member Functions:
- ```QDEntity(entity, deck=None)``` - Constructor from an entity, deck=None uses current deck
- ```QDEntity.convert(arg)``` - Static method, converts to QDEntity any instance itself or within a list/dict
- ```QDEntity.cards()``` - returns list of card names
- ```QDEntity.keys()``` - same as function cards()
- ```QDEntity.values()``` - returns list of values matching the cards/keys
- ```QDEntity.set_deck(deck)``` - Change entity deck (see ansa.constants)
- ```QDEntity.__len__()``` - len operator matching number if cards
- ```QDEntity.__getitem__()``` - overloading of [] operator for getting card values (see below)
- ```QDEntity.__setitem__()``` - overloading of [] operator for setting card values (see below)
- ```QDEntity.__iter__()``` - iterate over entity card,value pairs (see example)


Example:
```python
from ansa import base
from qd.ansa import QDEntity

# never forget the help ...
help(QDEntity)
# >>> A lot of text ...

entity_list = base.CollectEntities(base.CurrentDeck(), None, "GRID") # some model is already existing
entity_list = QDEntity.convert(entity_list) # converts single entities, lists and dicts
entity = entity_list[0] # choose first entity

entity.cards()
# >>> ['TYPE', 'NID', 'CP', 'X1', 'X2', 'X3', 'CD', 'PS', 'SEID', 'field 10', 'Name', 'FROZEN_ID', 'FROZEN_DELETE', 'AUXILIARY', 'Comment']

entity["TYPE"] # access like a dict
# >>> "GRID"

entity["X1","X2","X3"] # also lists work
# >>> [0.0, 20.0, 0.0]

entity["X1","X2","X3"] = [1., 19., 1.] # either string or list(str) setter
entity["X1","X2","X3"]
# >>> [1.0, 19.0, 1.0]

# error messages have always been missing ...
print(entity["UNKNOWN"])
# >>> KeyError: 'Key not found: UNKNOWN' 

# we can iterate over the entity, like a dictionary
for card_name, card_value in entity:
    pass
```


Constructor
```python
QDEntity.__init__(self, entity, deck=None)
```