import random
import pandas as pd
import streamlit as st
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
from utils import check_password
import logging


class Recipe:
    """Encapsulates an Amazon DynamoDB table of movie data."""
    def __init__(self, dyn_resource, month):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        :param month: The month selected by the user.
        """
        self.dyn_resource = dyn_resource
        self.table = self.dyn_resource.Table("Recipe")
        self.recipe = get_recipe_for_current_month(self.table, month, "Main dish")
        self.dessert = get_recipe_for_current_month(self.table, month, "Dessert")
        logging.info("The recipes have been downloaded")


@st.cache_resource
def get_recipe_for_current_month(_table, month, recipe_type):
    response = _table.scan(
        FilterExpression=Attr('Months').contains(month) & Attr("Type").eq(recipe_type)
    )
    items = response['Items']
    return items


def display_recipe(recipe):
    st.subheader(recipe["Name"])
    if "Link" in recipe.keys():
        st.write(recipe["Link"])
    if "Ingredients" in recipe:
        st.write(recipe["Ingredients"])


def select_random_recipe(bool_need_to_cook, recipe):
    return random.choice(recipe) if bool_need_to_cook else None


def display_dataframe_asking():
    st.subheader("Select when you need to prepare a meal:")
    number_of_lunch = pd.DataFrame([
        {"command": "Monday", "Diner": True, "Lunch": True, "Dessert for Diner": False, "Dessert for Lunch": False},
        {"command": "Tuesday", "Diner": True, "Lunch": True, "Dessert for Diner": False, "Dessert for Lunch": False},
        {"command": "Wednesday", "Diner": True, "Lunch": True, "Dessert for Diner": False, "Dessert for Lunch": False},
        {"command": "Thursday", "Diner": True, "Lunch": True, "Dessert for Diner": False, "Dessert for Lunch": False},
        {"command": "Friday", "Diner": True, "Lunch": True, "Dessert for Diner": False, "Dessert for Lunch": False},
        {"command": "Saturday", "Diner": False, "Lunch": False, "Dessert for Diner": True, "Dessert for Lunch": False},
        {"command": "Sunday", "Diner": False, "Lunch": False, "Dessert for Diner": False, "Dessert for Lunch": True},
    ])
    df = st.experimental_data_editor(number_of_lunch)
    return df


def display_result_dataframe(df):
    data = df.copy()
    data["Diner main dish"] = data["Diner"].map(lambda x: random.choice(Recipe.recipe)["Name"] if x else None)
    data["Launch main dish"] = data["Lunch"].map(lambda x: random.choice(Recipe.recipe)["Name"] if x else None)
    data["Diner dessert"] = data["Dessert for Diner"].map(
        lambda x: random.choice(Recipe.dessert)["Name"] if x else None)
    data["Launch dessert"] = data["Dessert for Lunch"].map(
        lambda x: random.choice(Recipe.dessert)["Name"] if x else None)
    data = data.drop(columns=["Diner", "Lunch", "Dessert for Diner", "Dessert for Lunch"])

    st.subheader("Your weekly meal planning:")
    st.experimental_data_editor(data, width=1000)

    return data


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


if __name__ == '__main__':
    logging.basicConfig(filename='logging.log')

    if check_password():
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        month = st.sidebar.slider("Change the month", 1, 12, datetime.now().month)
        dynamo_client = boto3.resource(service_name='dynamodb', region_name='eu-west-3')
        Recipe = Recipe(dynamo_client, month)

        df = display_dataframe_asking()
        data = display_result_dataframe(df)

        csv = convert_df(data)
        st.download_button(label="Download the table as CSV", data=csv, file_name="recipe_for_the_week.csv")
