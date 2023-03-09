import streamlit as st
import boto3
from utils import check_password


def check_item_in_database(db_table, recipe_name):
    response = db_table.get_item(
        Key={
            'Name': recipe_name
        }
    )
    return "Item" in response


def add_item(db_table, recipe_name, months):
    if not check_item_in_database(db_table, recipe_name):
        response = db_table.put_item(
            Item={
                "Name": recipe_name,
                "Month": months
            },
            ConditionExpression=f'attribute_not_exists({recipe_name})'
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            st.balloons()
            st.success("Item added to the database successfully.")
        else:
            st.error("Hoops, something strange has happen. Don't hesitate to send me the response written below:")
            st.write(response)
    else:
        st.warning("This recipe already exists in the database. Please use the update recipe page or change the name.")


if __name__ == '__main__':
    if check_password():
        dynamo_client = boto3.resource(service_name='dynamodb', region_name='eu-west-3')
        table = dynamo_client.Table("Recipe")

        st.header("Add a recipe to the database")
        name = st.text_input("Name: ")

        month = ["January", "February", "March", "April", "June", "July",
                 "August", "September", "October", "November", "December"]
        month_selected = st.multiselect("Select the month for this recipe:", month)
        month_index = [month.index(month_tmp) + 1 for month_tmp in month_selected]
        if st.button("Click to add to the database"):
            add_item(table, name, month_index)


