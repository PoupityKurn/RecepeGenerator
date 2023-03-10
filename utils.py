import streamlit as st


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True


def get_all_recipe(_dynamo_table):
    response = _dynamo_table.scan(ProjectionExpression='#name_id', ExpressionAttributeNames={'#name_id': 'Name'})
    recipes = [recipe["Name"] for recipe in response["Items"]]
    return recipes

def dataframe_to_ingredients(df):
    ingredients_name = list(df.Ingredients.astype("str"))
    quantity = list(df.Quantity.astype("str"))
    return {ingredients_name[i]: quantity[i] for i in range(len(ingredients_name))}
