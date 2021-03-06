"""Base class for patching time modules."""


class BasicPatcher(object):
    """Base class for patching time modules."""
    
    def __init__(self, clock, events_pool=None):
        """Create the patch."""
        self.clock = clock
        self.events_pool = events_pool
        
        self.patches = []
        
    @classmethod
    def get_events_namespace(cls):
        """Return the namespace of the patcher's events."""
        return None
    
    @classmethod
    def get_events_types(cls):
        """Return Enum of the patcher's events types."""
        return None
                
    def start(self):
        """Start mocking datetime module."""
        for p in self.patches:
            p.start()
            
    def stop(self):
        """Stop mocking datetime module."""
        for p in self.patches:
                p.stop()
