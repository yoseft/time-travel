"""A patch to the datetime module."""

from basic_patcher import BasicPatcher

import select as select_lib
from enum import Enum
import mock


class SelectPatcher(BasicPatcher):
    """Patcher for select module.
    
    patching:
        - select.select
    """
    
    EVENTS_NAMESPACE = 'select'
    EventTypes = Enum('select', 'READ WRITE EXCEPTIONAL')
    
    def __init__(self, *args, **kwargs):
        """Create the patch."""
        super(SelectPatcher, self).__init__(*args, **kwargs)
        
        self.select = mock.Mock(
            side_effect=self._mocked_select,
            spec=select_lib.select)
        
        self.patches = [mock.patch('select.select', self.select)]
        
    @classmethod
    def get_events_namespace(cls):
        """Return the namespace of the select events."""
        return cls.EVENTS_NAMESPACE
    
    @classmethod
    def get_events_types(cls):
        """Return Enum of select events types."""
        return cls.EventTypes 
        
    @staticmethod
    def _list_intersection(list1, list2):
        return list(set(list1).intersection(set(list2)))
    
    def _get_earliest_events(self, waited_events, events_type, timeout):
        added_timeout = float('inf') if timeout is None else timeout
        
        timeout_timestamp = self.clock.time + added_timeout
        
        result_events = []
        result_timestamp = timeout_timestamp
        
        for timestamp, events in self.events_pool.get_events(
                lambda etype: etype == events_type):
            if timestamp > timeout_timestamp:
                # No event before the timeout
                break
            
            triggering_events = set(waited_events).intersection(events) 
            
            if triggering_events:
                result_events = list(triggering_events)
                result_timestamp = timestamp
                break
            
        return result_timestamp, result_events
    
    def _mocked_select(self, rlist, wlist, xlist, timeout=None):
        read_timestamp, read_events = self._get_earliest_events(
            rlist,
            self.EventTypes.READ,
            timeout)
        write_timestamp, write_events = self._get_earliest_events(
            wlist,
            self.EventTypes.WRITE,
            timeout)
        ex_timestamp, ex_events = self._get_earliest_events(
            xlist,
            self.EventTypes.EXCEPTIONAL,
            timeout)
        
        timestamp = min([read_timestamp,
                         write_timestamp,
                         ex_timestamp])
        
        if timestamp == float('inf'):
            raise ValueError('No relevant future events were set fot infinite '
                             'timout')
        
        read_events = [] if timestamp < read_timestamp else read_events
        write_events = [] if timestamp < write_timestamp else write_events
        ex_events = [] if timestamp < ex_timestamp else ex_events
        
        self.events_pool.remove_events(timestamp,
                                       read_events,
                                       self.EventTypes.READ)
        self.events_pool.remove_events(timestamp,
                                       write_events,
                                       self.EventTypes.WRITE)
        self.events_pool.remove_events(timestamp,
                                       ex_events,
                                       self.EventTypes.EXCEPTIONAL)

        self.clock.time = timestamp
    
        return (read_events, write_events, ex_events)
