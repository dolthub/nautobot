from django.db.models.lookups import Contains

from nautobot.dcim.utils import object_to_path_node


class PathContains(Contains):
    def get_prep_lookup(self):
        self.rhs = [object_to_path_node(self.rhs)]
        return super().get_prep_lookup()
