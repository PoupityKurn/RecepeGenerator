import pandas as pd
import streamlit as st
import boto3
from utils import check_password, get_all_recipe, dataframe_to_ingredients


def get_recipe_details(table, recipe_name):
    response = table.get_item(Key={"Name": recipe_name})
    return response["Item"]


def update_recipe(table, name, recipe_type, months, url, ingredients):
    if ingredients and url:
        response = table.put_item(
            Item={"Name": name, "Type": recipe_type, "Months": months, "Link": url, "Ingredients": ingredients})
    elif ingredients and not url:
        response = table.put_item(
            Item={"Name": name, "Type": recipe_type, "Months": months, "Ingredients": ingredients})
    elif not ingredients and url:
        response = table.put_item(Item={"Name": name, "Type": recipe_type, "Months": months, "Link": url})
    else:
        response = table.put_item(Item={"Name": name, "Type": recipe_type, "Months": months})

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        st.balloons()
        st.success(f"The recipe {name} has been modified.")
    else:
        st.error("Hoops, something went wrong. Don't hesitate to send me the response written below:")
        st.write(response)


def add_new_recipe_and_remove_old_one(table, name, recipe_type, old_name, list_recipe, months, url, ingredients):
    if name in list_recipe:
        st.warning("This recipe name already exists in the database. Change the name to update the recipe")
    else:
        if ingredients and url:
            response = table.put_item(
                Item={"Name": name, "Type": recipe_type, "Months": months, "Link": url, "Ingredients": ingredients})
        elif ingredients and not url:
            response = table.put_item(
                Item={"Name": name, "Type": recipe_type, "Months": months, "Ingredients": ingredients})
        elif not ingredients and url:
            response = table.put_item(Item={"Name": name, "Type": recipe_type, "Months": months, "Link": url})
        else:
            response = table.put_item(Item={"Name": name, "Type": recipe_type, "Months": months})

        response_delete = table.delete_item(Key={"Name": old_name})

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200 \
                and response_delete["ResponseMetadata"]["HTTPStatusCode"] == 200:
            st.balloons()
            st.success(f"The recipe {old_name} has been modified and rename {name}.")
        else:
            st.error("Hoops, something went wrong. Don't hesitate to send me the responses written below:")
            st.write(response)
            st.write(response_delete)


def ingredients_to_dataframe(ingredients):
    if ingredients:
        return pd.DataFrame({"Ingredients": ingredients.keys(), "Quantity": ingredients.values()})
    else:
        return pd.DataFrame({"Ingredients": [""], "Quantity": [""]})


def change_item(table, recipe, list_recipe):
    name = recipe["Name"]
    type_index = 0 if recipe["Type"] == "Main dish" else 1
    current_url = recipe["Link"] if "Link" in recipe else ""
    months_dict = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7,
                   "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
    months_int_str = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July",
                      8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
    current_months = [months_int_str[month] for month in recipe["Months"]] if "Months" in recipe else []
    current_ingredients = recipe["Ingredients"] if "Ingredients" in recipe else None
    recipe_dataframe = ingredients_to_dataframe(current_ingredients)

    with st.form("Change the recipe"):
        name_changed = st.text_input("Name of the recipe:", name)
        recipe_type = st.radio("Main dish or dessert:", ("Main dish", "Dessert"), index=type_index)
        url = st.text_input("URL of the recipe (optional):", current_url)
        months = st.multiselect("Months for this recipe:", months_dict.keys(), current_months)

        st.markdown("<style>.small-font {font-size:14px;}</style>", unsafe_allow_html=True)
        st.markdown('<p class="small-font">Change the table below to update the ingredients:</p>',
                    unsafe_allow_html=True)
        df_ingredients_modified = st.experimental_data_editor(recipe_dataframe, num_rows="dynamic")
        ingredients_changed = dataframe_to_ingredients(df_ingredients_modified)

        submitted = st.form_submit_button("Submit")
        if submitted:
            months_selected = [months_dict[month] for month in months]
            if not months_selected:
                st.error("The recipe has not been edited. Please fill in the months for this recipe.")
            else:
                if name_changed == name:
                    update_recipe(table, name_changed, recipe_type, months_selected, url, ingredients_changed)
                else:
                    add_new_recipe_and_remove_old_one(table, name_changed, recipe_type, name, list_recipe,
                                                      months_selected, url, ingredients_changed)


if __name__ == '__main__':
    if check_password():
        st.header("Use this page to edit a recipe")
        dynamo_client = boto3.resource(service_name='dynamodb', region_name='eu-west-3')
        table = dynamo_client.Table("Recipe")

        list_recipe = get_all_recipe(table)
        recipe_selected = st.sidebar.selectbox("Select a recipe to change: ", list_recipe)
        recipe = get_recipe_details(table, recipe_selected)
        change_item(table, recipe, list_recipe)
