
# PYTHON script
import os
import ansa
import numpy as np
from ansa import base
from ansa import constants


class QDEntity(base.Entity):
	
    ## Construct a QDEntity from an ANSA entity
    #
    # @param ansa.base.Entity entity
    # @param int deck=None : entity deck, if ommited current will be used
    def __init__(self, entity, deck=None):

        self.set_deck(deck)
        super().__init__(self.myDeck, entity._id, entity._ansaType(0))

    
#    def __init__(self,id,entity_type,deck=None):
#        self.set_deck(deck)
#        super().__init__(deck, id, entity_type)
    

    ## Set the deck of the entity
    #
    # @param int deck : use values in ansa.constants
    def set_deck(self, deck):
        if deck:
            self.myDeck = deck
        else:
            self.myDeck = base.CurrentDeck()

    
    ## Get the entity card labels (not values)
    #
    # @return list(str) keys : list of card names
    def keys(self):
        return self.cards()


    ## Get the entity card values
    #
    # @return list(str) values : list of card values
    def values(self):
        return self[self.cards()]

    
    ## Get the entity card labels (not values)
    #
    # @return list(str) keys : list of card names
    def cards(self):
        return self._cardFields(self.myDeck)
	
    ## Returns number of cards
    #
    # @return int nCards
    def __len__(self):
        return len(self._cardFields(self.myDeck))
		
    
    ## Get card values by their name
    #
    # @param str/list(str) arg : card name or list-like object of card names to query
    # @return object/list(str) ret : returns card value or list with card values
    def __getitem__(self, key):

        # just a string key
        if isinstance(key, str):
            ret = base.GetEntityCardValues(self.myDeck, self, [key])
            if ret:
                return ret[key]
            else:
                raise KeyError('Key not found: %s' % str(key))
        
        # list of string key
        elif isinstance(key, (list,tuple,np.ndarray)):
            
            ret = base.GetEntityCardValues(self.myDeck, self, key)
            
            # check if all cards could be found
            if len(ret) == len(key):
                return [ret[key[ii]] for ii in range(len(key)) ]
            
            # some cards could not be found
            else:

                unknown_keys = [ subkey for subkey in key if subkey not in ret]
                #unknown_keys = [ subkey for subkey in key if 0==len(base.GetEntityCardValues(self.myDeck, self, [subkey])) ]
                if unknown_keys:
                    raise KeyError("Could not find the following cards: %s" % str(unknown_keys))
                else:
                    raise KeyError("Some key (unknown) was not found in %s" % str(key))
        
        # unknown key type
        else:
            raise TypeError("key must be of type string or list(str)/tuple(str)/np.ndarray(str), not %s." % str(type(key)))

    
    ## Overloaded [] opeartor for setting entitiy cards
    #
    # @param str/list(str) key : card name or list of names
    # @param object/list(object) value : 
    def __setitem__(self, key, value):
		
        # just a string key
        if isinstance(key, str):
            
            if base.SetEntityCardValues(self.myDeck, self, {key:value}) != 0: # error
                raise KeyError('Key-Value %s could not be set.' % str({key:value}))

        # list of string key
        elif isinstance(key, (list,tuple,np.ndarray)):

            if len(key) != len(value):
                raise ValueError("len(keys) != len(values) : %d != %d" % (len(key), len(values)) )
            
            if base.SetEntityCardValues(self.myDeck, self, dict(zip(key, value))) != 0: # error

                unknown_keys = [ key[ii] for ii in range(len(key)) if 0!=base.SetEntityCardValues(self.myDeck, self, {key[ii]:value[ii]}) ]
                if unknown_keys:
                    raise KeyError("Could not set the following cards: %s" % str(unknown_keys))
                else:
                    raise KeyError("Some unknown fields could not be set from %s" % str(key))

        # unknown key type
        else:
            raise TypeError("key must be of type string or list(str)/tuple(str)/np.ndarray(str), not %s." % str(type(key)))
			
    
    ## Iterator over the entity
    #
    # @return dict-iterator iter : iterator over key,value pairs
    #
    # The key is the card name, whereas the value is the card value ... obviously
    def __iter__(self):
        cards = self.cards()
        return iter(dict(zip(cards,self[cards])).items())


    ## Conver any object or container with ansa.base.Entity to QDEntity
    #
    # @param base.Entity/list(any)/dict(any) arg : entity or container with entities
    # @return QDEntity/list(any)/dict(any) ret : converted argument
    #
    # This function converts an ansa entity to a qd entity. If a list or dict is given, any 
    # entity within is converted WHILE ALL OTHER ENTRIES STAY UNTOUCHED! 
    # With this function, containers, which may contain entities can be converted
    # in a very comfortabel way.
    @staticmethod
    def convert(arg):

        if isinstance(arg, base.Entity):
            return QDEntity(arg)

        elif isinstance(arg, (list,tuple)):
            return [QDEntity(entry) if isinstance(entry, base.Entity) else entry for entry in arg]

        elif isinstance(arg, dict):
            return {QDEntity(key) if isinstance(key, base.Entity) else value : 
                    QDEntity(value) if isinstance(value, base.Entity) else value for key,value in arg.items()}

        else:
            raise ValueError("Argument is neither a ansa.base.Entity, nor a list/dict.")

    
    ## Similar to ansa.base.CollectEntities, but more convenient
    #
    # @param str entity_type : search type, e.g. "NODE"
    # @param str container : reference to a container entity or list of container entities
    # @param int deck : ansa deck used, see ansa.constants
    # @param **kwargs : further optional arguments for CollectEntities
    #
    # This is a comfort wrapper for collection of entities in the qd environment. One just has
    # to specify the type, everything else is optional. The entities are directly converted
    # to QDEntities. 
    # Further optional arguments are directly forwarded to base.CollectEntities!
    #
    # based on: ansa.base.CollectEntities(deck, containers, search_types, recursive, filter_visible, prop_from_entities, mat_from_entities)
    @staticmethod
    def collect(search_type, container=None, deck=base.CurrentDeck(), **kwargs):
        return QDEntity.convert(base.CollectEntities( *(deck, container, search_type), **kwargs))

    
    ## Get an entity in the database
    # 
    # @param str entity_type : search type, e.g. "NODE"
    # @param int element_id : id of the element to search
    # @param int deck : ansa deck used, see ansa.constants
    # @param **kwargs : further optional arguments for GetEntity
    # 
    # based on: ansa.base.GetEntity(deck, type, element_id, location)
    @staticmethod
    def get(search_type, element_id, deck=base.CurrentDeck(), **kwargs):
        return QDEntity.convert( base.GetEntity( *(deck, search_type, element_id), **kwargs) )
