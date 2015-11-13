
from py.test import raises
from pytest import raises

from graphene import Interface, ObjectType, Schema
from graphene.core.fields import Field, ListField, StringField
from graphql.core import graphql
from graphql.core.type import (GraphQLInterfaceType, GraphQLObjectType,
                               GraphQLSchema)
from tests.utils import assert_equal_lists

schema = Schema(name='My own schema')


class Character(Interface):
    name = StringField()


class Pet(ObjectType):
    type = StringField(resolve=lambda *_: 'Dog')


class Human(Character):
    friends = ListField(Character)
    pet = Field(Pet)

    def resolve_name(self, *args):
        return 'Peter'

    def resolve_friend(self, *args):
        return Human(object())

    def resolve_pet(self, *args):
        return Pet(object())

schema.query = Human


def test_get_registered_type():
    assert schema.get_type('Character') == Character


def test_get_unregistered_type():
    with raises(Exception) as excinfo:
        schema.get_type('NON_EXISTENT_MODEL')
    assert 'not found' in str(excinfo.value)


def test_schema_query():
    assert schema.query == Human


def test_query_schema_graphql():
    object()
    query = '''
    {
      name
      pet {
        type
      }
    }
    '''
    expected = {
        'name': 'Peter',
        'pet': {
            'type': 'Dog'
        }
    }
    result = graphql(schema.schema, query, root=Human(object()))
    assert not result.errors
    assert result.data == expected


def test_query_schema_execute():
    object()
    query = '''
    {
      name
      pet {
        type
      }
    }
    '''
    expected = {
        'name': 'Peter',
        'pet': {
            'type': 'Dog'
        }
    }
    result = schema.execute(query, root=object())
    assert not result.errors
    assert result.data == expected


def test_schema_get_type_map():
    assert_equal_lists(
        schema.schema.get_type_map().keys(),
        ['__Field', 'String', 'Pet', 'Character', '__InputValue', '__Directive',
            '__TypeKind', '__Schema', '__Type', 'Human', '__EnumValue', 'Boolean']
    )


def test_schema_no_query():
    schema = Schema(name='My own schema')
    with raises(Exception) as excinfo:
        schema.schema
    assert 'define a base query type' in str(excinfo)


def test_schema_register():
    schema = Schema(name='My own schema')

    @schema.register
    class MyType(ObjectType):
        type = StringField(resolve=lambda *_: 'Dog')

    schema.query = MyType

    assert schema.get_type('MyType') == MyType


def test_schema_register():
    schema = Schema(name='My own schema')

    @schema.register
    class MyType(ObjectType):
        type = StringField(resolve=lambda *_: 'Dog')

    with raises(Exception) as excinfo:
        schema.get_type('MyType')
    assert 'base query type' in str(excinfo.value)


def test_schema_introspect():
    schema = Schema(name='My own schema')

    class MyType(ObjectType):
        type = StringField(resolve=lambda *_: 'Dog')

    schema.query = MyType

    introspection = schema.introspect()
    assert '__schema' in introspection