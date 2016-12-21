
# qd-ansa 

This library is a python utility library for ANSA from Beta CAE Systems SA. The project is not affiliated in any way with the official software. 

These enhancements make access much easier, and also debugging! This module was written for the reason, that the common scripting API did not feel pythonic enough to me. 

# Installation

Just copy the fles into your installation folder: /Path/to/BETA_CAE_Systems/shared_v17.0.2/python/win64/Lib/site-packages

# Classes



## QDEntity

| Member Function | Short Explanation |
| --- | --- |
| ```QDEntity(entity, deck=None)``` | Constructor from a ```ansa.base.Entity```
| ```QDEntity.convert(arg)``` | Static function for conversion of an entity or containers
| ```QDEntity.cards()``` | Get all of the entities card names as ```list(str)```
| ```QDEntity.keys()``` | Same as ```QDEntity.cards()```
| ```QDEntity.values()``` | Get all of the entities card values as ```list```
| ```QDEntity.set_deck(deck)``` | Set the entity deck manually, use ```ansa.constants```
| ```QDEntity.__len__()``` | Overloaded ```len```, returns numbe of cards
| ```QDEntity.__getitem__()``` | Overloaded ```[]```, access entity cards like a dictionary, also accepts lists
| ```QDEntity.__setitem__()``` | Overloaded ```[]```, change single or multiple card values directly
| ```QDEntity.__iter__()``` | Overloaded iterator for loops, iterate over card names and values in the entity

------------------

### ```QDEntity(entity, deck=None)```

Constructor of a ```QDEntity``` from an ```ansa.base.Entity```. Deck can be specified with ```ansa.constants``` and uses ```base.CurrentDeck()``` if not specified.

```python
ansa_entity = ansa.base.Entity(deck=base.CurrentDeck(), id=1, type="GRID")
qd_entity = QDEntity(ansa_entity)
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


### Full Example:

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
