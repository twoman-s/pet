from rest_framework import serializers


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        extra_fields = kwargs.pop("override_fields", [])
        assert (
            type(extra_fields) == list
        ), 'Class {serializer_class} "override_fields" kwarg must a list'.format(
            serializer_class=self.__class__.__name__
        )

        super().__init__(*args, **kwargs)

        existing = set(self.fields.keys())
        allowed = set(extra_fields)

        context = self.context.get("request")
        if context:
            fields = context.query_params.get("fields")
            if fields:
                fields = fields.split(",")
                allowed = set(fields) | allowed
                self._remove_fields(existing - allowed)
            return

        # allow all existing fields if none provided. ie, extra_fields is empty
        if not len(allowed):
            allowed = existing
        # remove the non-allowed fields
        self._remove_fields(existing - allowed)

    def _remove_fields(self, fields):
        for field_name in fields:
            self.fields.pop(field_name)
