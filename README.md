
# qd-ansa 

This library is a python utility library for ANSA and META from Beta CAE Systems SA. The project is not affiliated in any way with the official software. 

These enhancements make access much easier, and also debugging! This module was written for the reason, that the common scripting API did not feel pythonic enough to me. 

Authors: D. Toewe, C. Diez

# Installation

Just copy the fles into your installation folder: /Path/to/BETA_CAE_Systems/shared_v17.0.2/python/win64/Lib/site-packages

# META Example

The META API has currently only one function, which exports your current model to an html file. Currently only shell elements are supported.

```python
from qd.meta.export import export_to_html

export_to_html("Filepath/for/HTML", use_fringe=True, fringe_bounds=[0,0.03] )
```

[See Example 1](./examples/model_rail.html)

[See Example 2](./examples/model_silverado.html)

# ANSA Example

```python
from ansa import base
from qd.ansa import QDEntity

# never forget the help ...
help(QDEntity)
# >>> A lot of text ...

# NOTE:
# Some ANSA Model is already open

ansa_entity_list = base.CollectEntities(base.CurrentDeck(), None, "GRID") # method from ANSA
qd_entity_list = QDEntity.convert(ansa_entity_list) # converts single entities, lists and dicts
qd_entity_list = QDEntity.collect("GRID") # get them directly, more comfortable :)

entity = QDEntity.get("NODE", 1) # get an entity directly

entity.cards()
# >>> ['TYPE', 'NID', 'CP', 'X1', 'X2', 'X3', 'CD', 'PS', 'SEID', 'field 10', 'Name', 'FROZEN_ID', 'FROZEN_DELETE', 'AUXILIARY', 'Comment']

entity["TYPE"] # access like a dict
# >>> "GRID"

entity["X1","X2","X3"] # also lists work
# >>> [0.0, 20.0, 0.0]

entity["X1","X2","X3"] = [1., 19., 1.] # either string or list(str) setter
entity["X1","X2","X3"]
# >>> [1.0, 19.0, 1.0]

# error messages ...
print(entity["UNKNOWN"])
# >>> KeyError: 'Key not found: UNKNOWN' 

# we can iterate over the entity, like a dictionary
for card_name, card_value in entity:
    pass
```

# Classes

## QDEntity

| Static Functions | Short Explanation |
| --- | --- |
| ```QDEntity.create(entity_type, deck=base.CurrentDeck(), **card_properties)``` | Static function for entity creation
| ```QDEntity.convert(arg)``` | Static function for conversion of an entity or containers
| ```QDEntity.collect(search_type, container=None, deck=base.CurrentDeck(), **kwargs)``` | Static function for collecting entities from the database
| ```QDEntity.get(search_type, element_id, deck=base.CurrentDeck(), **kwargs)``` | Static function for getting an element from its type and id

###

| Member Functions | Short Explanation |
| --- | --- |
| ```QDEntity(entity, deck=None)``` | Constructor from an ```ansa.base.Entity```
| ```QDEntity.__len__()``` | Overloaded ```len```, returns numbe of cards
| ```QDEntity.__getitem__(key)``` | Overloaded ```[]```, access entity cards like a dictionary, also accepts lists
| ```QDEntity.__setitem__(key, value)``` | Overloaded ```[]```, change single or multiple card values directly
| ```QDEntity.__iter__()``` | Overloaded iterator for loops, iterate over card names and values in the entity
| ```QDEntity.collect(search_type, deck=self.myDeck, **kwargs)``` | Collect entities, container is the instance itself
| ```QDEntity.cards()``` | Get all of the entities card names as ```list(str)```
| ```QDEntity.keys()``` | Same as ```QDEntity.cards()```
| ```QDEntity.values()``` | Get all of the entities card values as ```list```
| ```QDEntity.set_deck(deck)``` | Set the entity deck manually, use ```ansa.constants```
| ```QDEntity.user_edit()``` | Pops the entity card for the user for editation.
------------------

## Detailed Description

### ```QDEntity.create(entity_type, deck=base.CurrentDeck(), **card_properties)```

This static method creates a QDEntity. It is a wrapper for ```base.CreateEntity```. One has to specify solely the Type. 
All other optional arguments are passed as a dictionary to the function, so that attribtues may be set directly.

```python
qd_entity = QDEntity.create("GRID") # create a grid
qd_entity = QDEntity.create("GRID", X1=10, X2=20, X3=10) # create a grid with values
```

### ```QDEntity.convert(arg)```

This static method converts any ```ansa.base.Entity``` or any entity within a container (list,tuple,np.array,dict). All other container elements stay untouched!

```python
ansa_entity = ansa.base.Entity(deck=base.CurrentDeck(), id=1, type="GRID")
qd_entity = QDEntity.convert(ansa_entity)

entity_list = [ansa_entity,"YAY"]
entity_list = QDEntity.convert(entity_list) # "YAY" stays untouched

entity_dict = { ansa_entity._id : ansa_entity } # some dictionary
entity_dict= QDEntity.convert(ansa_entity) # converts keys/values if ansa entity
```

### ```QDEntity.collect(search_type, container=None, deck=base.CurrentDeck(), **kwargs)```

This static method is a wrapper for ```ansa.base.CollectEntities```. It's a little more comfortable, since it does not require as many arguments. The Entities are returned as ```QDEntity```.

```python
qd_entities = QDEntity.collect("FACE")
```

### ```QDEntity.get(search_type, element_id, deck=base.CurrentDeck(), **kwargs)```

This static method is a wrapper for ```ansa.base.GetEntity```. One may get an entity from
its type and id. 

```python
qd_entity_face = QDEntity.get("FACE", 1)
```

### ```QDEntity(entity, deck=None)```

Constructor of a ```QDEntity``` from an ```ansa.base.Entity```. Deck can be specified with ```ansa.constants``` and uses ```base.CurrentDeck()``` if not specified.

```python
ansa_entity = ansa.base.Entity(deck=base.CurrentDeck(), id=1, type="GRID")
qd_entity = QDEntity(ansa_entity)
```

### ```QDEntity.__len__()```

Overloaded len operator. Returns the number of cards of the entity.

```python
len(qd_entity)
# >>> 7
```

### ```QDEntity.__getitem__(key)```

Oerloaded [] operator. Any card in the entity can now be accessed like a dictionary. The argument may be either a ```str``` or a ```list(str)```. In the second case a list is returned.

```python
qd_entity["TYPE"] # entity is a mesh node
# >>> 'GRID'
qd_entity["NID"]
# >>> 1
qd_entity["TYPE","NID"] # also lists work
# >>> ['GRID',1]

# everyone loves meaningful error messages :)
qd_entity["TYPE","NID","WRONG_FIELD"]
# >>> KeyError: "Could not find the following keys: ['WRONG_FIELD']"
```

### ```QDEntity.__setitem__(key, value)```

Overloaded [] operator for setting card values.

```python
qd_entity["X1"] # entity is a mesh node
# >>> 0.0
qd_entity["X1"] = 1 # single setter
qd_entity["X1","X2"] = 1,19 # list setter

# intelligent error messages ... that's rare ...
qd_entity["X1","X2","WRONG_FIELD"] = 1,19,"YAY" 
# >>> KeyError: "Could not set the following cards: ['WRONG_FIELD']"
```

### ```QDEntity.__iter__()```

Overlaoded operator for loops. With this, one can iterate over the ```ansa.base.Entity``` and gets card names and values as pair.

```python
for card_name,card_value in qd_entity:
    print("%s : %s" % (card_name,card_value) )
# >>> 'TYPE' : 'GRID'
# >>> 'NID' : 1
# >>> ...
```

### ```QDEntity.collect(search_type, deck=self.myDeck, **kwargs)```

Same as collect entities, but the container is the instance itself. For the generic 
collect, call the static function from the class, not the instance. 

```python
qd_entities = QDEntity.collect("FACE") # static function collect
face = qd_entities[0] # choose first face
face_grids = face.collect("GRID") # collect GRIDS of face only!
```

### ```QDEntity.cards()``` or ```QDEntity.keys()```

Get all the card values of an entity as a list of str.

```python
qd_entity.cards() # this qd_entity is a "NODE"
# >>> ['TYPE', 'NID', ... ] 
```

### ```QDEntity.values()```

Get all the values for the cards as a list of objects.

```python
qd_entity.values() # this qd_entity is a "NODE"
# >>> ['GRID', 1, ... ]
```

### ```QDEntity.set_deck(deck)```

Set the deck of the entity. Use ```ansa.constants```.

```python
qd_entity.set_deck(ansa.constants.ABAQUS)
```

### ```QDEntity.user_edit()```

Pops up the card of the entity, so that the user can edit it. Returns, whether the user pressed ok (True) or not (False).

```python
qd_entity = QDEntity.get("FACE",1)
qd_entity.user_edit() # pops up the dialog
```
