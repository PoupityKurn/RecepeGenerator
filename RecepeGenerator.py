import random

# import polars as pl
import pandas as pd
import streamlit as st
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime


class Recipe:
    """Encapsulates an Amazon DynamoDB table of movie data."""
    def __init__(self, dyn_resource, month):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        :param month: The month selected by the user.
        """
        self.dyn_resource = dyn_resource
        self.table = self.dyn_resource.Table("Recipe")
        self.recipe = get_recipe_for_current_month(self.table, month, "Main dishes")


@st.cache_resource
def get_recipe_for_current_month(_table, month, recipe_type):
    response = _table.scan(
        FilterExpression=Attr('Month').contains(month) & Attr("Type").eq("Main dish")
    )
    items = response['Items']
    return items


def display_recipe(recipe):
    st.subheader(recipe["Name"])
    if "Link" in recipe.keys():
        st.write(recipe["Link"])
    if "Ingredients" in recipe:
        st.write(recipe["Ingredients"])


if __name__ == '__main__':
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    st.write("")
    number_of_lunch = pd.DataFrame([
        {"command": "Monday", "Diner": True, "Lunch": False, "Dessert for Diner": False, "Dessert for Lunch": False},
        {"command": "Tuesday", "Diner": True, "Lunch": False, "Dessert for Diner": False, "Dessert for Lunch": False},
        {"command": "Wednesday", "Diner": True, "Lunch": False, "Dessert for Diner": False, "Dessert for Lunch": False},
        {"command": "Thursday", "Diner": True, "Lunch": False, "Dessert for Diner": False, "Dessert for Lunch": False},
        {"command": "Friday", "Diner": True, "Lunch": False, "Dessert for Diner": False, "Dessert for Lunch": False},
        {"command": "Saturday", "Diner": False, "Lunch": False, "Dessert for Diner": False, "Dessert for Lunch": False},
        {"command": "Sunday", "Diner": False, "Lunch": False, "Dessert for Diner": False, "Dessert for Lunch": False},
    ])
    df = st.experimental_data_editor(number_of_lunch)
    month = st.sidebar.slider("Change the month", 1, 12, datetime.now().month)
    dynamo_client = boto3.resource(service_name='dynamodb', region_name='eu-west-3')
    Recipe = Recipe(dynamo_client, month)
    for day in days_of_week:
        st.header(day)
        # TODO: Separate dessert and main dish
        display_recipe(random.choice(Recipe.recipe))

