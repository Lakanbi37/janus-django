import graphene

from api.graphql.apps import AppQuery, AppMutation


schema = graphene.Schema(query=AppQuery, mutation=AppMutation)