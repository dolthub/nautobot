from django.db.models import Aggregate, JSONField, Value


class JSONBAgg(Aggregate):
    function = None
    output_field = JSONField()

    # borrowed from django.contrib.postrgres.aggregats.JSONBagg
    def convert_value(self, value, expression, connection):
        if not value:
            return '[]'
        return value

    def as_sql(self, compiler, connection, **extra_context):
        engine = connection.settings_dict['ENGINE']
        if not JSONBAgg.function:
            if 'postgres' in engine:
                JSONBAgg.function = 'JSONB_AGG'
            elif 'mysql' in engine:
                JSONBAgg.function = 'JSON_ARRAYAGG'
            else:
                raise ConnectionError("Only Postgres and MySQL supported")
        return super().as_sql(compiler, connection, **extra_context)


class OrderableJSONBAgg(JSONBAgg):
    """
    TODO in Django 3.2 ordering is supported natively on JSONBAgg so this is no longer needed.
    """

    template = "%(function)s(%(distinct)s%(expressions)s %(ordering)s)"


class EmptyGroupByJSONBAgg(JSONBAgg):
    """
    JSONBAgg is a builtin aggregation function which means it includes the use of a GROUP BY clause.
    When used as an annotation for collecting config context data objects, the GROUP BY is
    incorrect. This subclass overrides the Django ORM aggregation control to remove the GROUP BY.

    TODO in Django 3.2 ordering is supported natively on JSONBAgg so we only need to inherit from JSONBAgg.
    """

    contains_aggregate = False
