import streamlit as st
import boto3
from utils import check_password, dataframe_to_ingredients
import pandas as pd


def check_item_in_database(db_table, recipe_name):
    response = db_table.get_item(
        Key={
            'Name': recipe_name
        }
    )
    return "Item" in response


def add_item(table, name, recipe_type, months, url, ingredients):
    if not check_item_in_database(table, name):
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
            st.success(f"The recipe {name} has been created.")
        else:
            st.error("Hoops, something went wrong. Don't hesitate to send me the response written below:")
            st.write(response)
    else:
        st.warning("This recipe already exists in the database. Please use the update recipe page or change the name.")


if __name__ == '__main__':
    if check_password():
        dynamo_client = boto3.resource(service_name='dynamodb', region_name='eu-west-3')
        table = dynamo_client.Table("Recipe")

        st.header("Add a recipe to the database")
        with st.form("Change the recipe"):
            name = st.text_input("Name of the recipe:")
            recipe_type = st.radio("Main dish or dessert:", ("Main dish", "Dessert"))
            url = st.text_input("URL of the recipe (optional):")

            months_dict = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7,
                           "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
            months = st.multiselect("Months for this recipe:", months_dict.keys())

            recipe_dataframe = pd.DataFrame({"Ingredients": [""], "Quantity": [""]})
            st.markdown("<style>.small-font {font-size:14px;}</style>", unsafe_allow_html=True)
            st.markdown('<p class="small-font">Change the table below to update the ingredients:</p>',
                        unsafe_allow_html=True)
            df_ingredients_modified = st.experimental_data_editor(recipe_dataframe, num_rows="dynamic")
            ingredients = dataframe_to_ingredients(df_ingredients_modified)
            submitted = st.form_submit_button("Submit")
            if submitted:
                months_selected = [months_dict[month] for month in months]
                if not months_selected:
                    st.error("The recipe has not been edited. Please fill in the months for this recipe.")
                else:
                    add_item(table, name, recipe_type, months_selected, url, ingredients)
