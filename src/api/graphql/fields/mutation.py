from django.db.models import Model
from django.shortcuts import get_object_or_404
from graphene import relay
from graphene.types.base import BaseOptions
from graphql_relay import from_global_id


class BaseMutationOptions(BaseOptions):
    model = None  # type: Model
    lookup_field = None
    fields = None
    name = None


class BaseMutation(relay.ClientIDMutation):

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
            cls, model=None, lookup_field=None, _meta=None, output=None, input_fields=None, arguments=None, name=None,
            **options
    ):
        cls.instance = None
        if model is None:
            raise Exception("{} expected a model class inserted".format(cls.__class__.__name__))
        if lookup_field is None and model:
            lookup_field = model._meta.pk.name
        if not _meta:
            _meta = BaseMutationOptions(cls)
        _meta.model = model
        _meta.lookup_field = lookup_field
        super(BaseMutation, cls).__init_subclass_with_meta__(
            output=output, input_fields=input_fields, arguments=arguments, name=name, _meta=_meta, **options
        )

    @classmethod
    def get_mutation_kwargs(cls, root, info, **input):
        lookup_field = cls._meta.lookup_field
        model = cls._meta.model
        filter_kwargs = {}
        if lookup_field in input:
            filter_kwargs[lookup_field] = input[lookup_field]
            if lookup_field == "id":
                _, id_ = from_global_id(input[lookup_field])
                filter_kwargs[lookup_field] = id_
            cls.instance = get_object_or_404(model, **filter_kwargs)
            return {
                "instance": cls.instance,
                "data": input,
                "request": info.context,
                "partial": True
            }
        return {"data": input, "request": info.context}

    @classmethod
    def save(cls, root, info, **input):
        kwargs = cls.get_mutation_kwargs(root, info, **input)
        if kwargs.get("instance"):
            return cls.update(**kwargs)
        return cls.create(**kwargs)

    @classmethod
    def mutate_and_get_payload(cls, root, info, data):
        return cls.save(root, info, **data)

    @classmethod
    def create(cls, request, data):
        """"""
        raise NotImplementedError(
            "{0} must implement a create method to create {1} instance".format(
                cls.__class__.__name__,
                cls._meta.model.__class__.__name__
            )
        )

    @classmethod
    def update(cls, instance, request, partial, data):
        """"""
        raise NotImplementedError(
            "{0} must implement a update method to Edit/Update {1} instance".format(
                cls.__class__.__name__,
                instance
            )
        )
