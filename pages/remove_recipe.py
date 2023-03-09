from utils import check_password, get_all_recipe
import boto3
import streamlit as st

if __name__ == '__main__':
    if check_password():
        st.header("Use this page to edit a recipe")
        dynamo_client = boto3.resource(service_name='dynamodb', region_name='eu-west-3')
        table = dynamo_client.Table("Recipe")

        list_recipe = get_all_recipe(table)
        recipe_selected = st.selectbox("Select a recipe to change: ", list_recipe)
        if st.button(f"Remove the recipe {recipe_selected}"):
            response_delete = table.delete_item(Key={"Name": recipe_selected})
            if response_delete["ResponseMetadata"]["HTTPStatusCode"] == 200:
                st.balloons()
                st.success(f"The recipe {recipe_selected} has been removed.")
            else:
                st.error("Hoops, something went wrong. Don't hesitate to send me the responses written below:")
                st.write(response_delete)
