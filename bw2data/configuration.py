import platform

DEFAULT_PROCESS_NODE_TYPE = "process"
PROCESS_NODE_TYPES = [
    "process",
    None,
]
VALID_LCI_NODE_TYPES = [
    "process",
    "emission",
    "natural resource",
    "product",
    "economic",
    "inventory indicator",
]
VALID_EXCHANGE_TYPES = [
    'biosphere',
    'production', 'substitution', 'generic production',
    'technosphere', 'generic consumption',
]
VALID_ACTIVITY_KEYS = [
    'CAS number',
    'activity',
    'activity type',
    'authors',
    'categories',
    'classifications',
    'code',
    'comment',
    'created',
    'database',
    'exchanges',
    'filename',
    'flow',
    'id',
    'location',
    'modified',
    'name',
    'parameters',
    'production amount',
    'reference product',
    'synonyms',
    'tags',
    'type',
    'unit',
]
VALID_EXCHANGE_KEYS = [
    'activity',
    'amount',
    'classifications',
    'code',
    'comment',
    'flow',
    'input',
    'loc',
    'maximum',
    'minimum',
    'name',
    'output',
    'pedigree',
    'production volume',
    'properties',
    'scale',
    'scale without pedigree',
    "shape",
    "temporal_distribution",
    'type',
    'uncertainty type',
    'uncertainty_type',
    'unit',
]


class Config:
    """A singleton that stores configuration settings"""

    version = 3
    backends = {}
    cache = {}
    metadata = []
    sqlite3_databases = []
    _windows = platform.system() == "Windows"

    @property
    def biosphere(self):
        """Get name for ``biosphere`` database from user preferences.

        Default name is ``biosphere3``; change this by changing ``config.p["biosphere_database"]``."""
        return self.p.get("biosphere_database", "biosphere3")

    @property
    def global_location(self):
        """Get name for global location from user preferences.

        Default name is ``GLO``; change this by changing ``config.p["global_location"]``."""
        return self.p.get("global_location", "GLO")


config = Config()
