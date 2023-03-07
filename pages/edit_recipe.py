import pandas as pd
import streamlit as st
import boto3
from boto3.dynamodb.conditions import Key, Attr


@st.cache_resource()
def get_all_recipe(_dynamo_table):
    response = _dynamo_table.scan(ProjectionExpression='#name_id', ExpressionAttributeNames={'#name_id': 'Name'})
    recipes = [recipe["Name"] for recipe in response["Items"]]
    return recipes


def get_recipe_details(table, recipe_name):
    response = table.get_item(Key={"Name": recipe_name})
    return response["Item"]


def update_recipe(table, name, recipe_type, url=None, ingredients=None):
    table.update_item(key={"Name": name, "Type": recipe_type})


def add_new_recipe_and_remove_old_one(table, name, recipe_type, old_name, list_recipe, url=None, ingredients=None):
    if name in list_recipe:
        st.warning("This recipe name already exists in the database. Change the name to update the recipe")
    else:
        response = table.put_item(
            Item={
                "Name": name,
                # "Month": months
            }
        )
        table.delete_item(old_name)


def change_item(table, recipe, list_recipe):
    name = recipe["Name"]
    with st.form("Change the recipe"):
        name_changed = st.text_input("Change the name", name)
        type_index = 0 if recipe["Type"] == "Main dish" else 1
        recipe_type = st.radio("Main dish or dessert", ("Main dish", "Dessert"), index=type_index)
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write(name_changed == name)
            if name_changed == name:
                update_recipe(table, name_changed, recipe_type)
            else:
                add_new_recipe_and_remove_old_one(table, name_changed, recipe_type, list_recipe)


if __name__ == '__main__':
    dynamo_client = boto3.resource(service_name='dynamodb', region_name='eu-west-3')
    table = dynamo_client.Table("Recipe")
    list_recipe = get_all_recipe(table)
    recipe_selected = st.sidebar.selectbox("Select a recipe to change: ", list_recipe)
    recipe = get_recipe_details(table, recipe_selected)
    change_item(table, recipe, list_recipe)

