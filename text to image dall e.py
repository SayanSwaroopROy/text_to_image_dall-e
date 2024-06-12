# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 01:00:54 2024

@author: sayan
"""

from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO

def accept_prompt(con=0):

    """
    Accepts user input for image description and image size code.

    Parameters:
        con (int): Indicates the type of prompt to accept.
                   0: Accept both image description and image size code.
                   1: Accept only image description.
                   2: Accept only image size code.

    Returns:
        tuple: If `con` is 0, returns a tuple containing image description and image size code.
               If `con` is 1, returns only the image description.
               If `con` is 2, returns only the image size code.

    Raises:
        Any exceptions that occur during the execution of the function are caught and printed.
    """
    
    try:
        if con==0:
            print("Enter 'STOP' to exit")
            prompt=input("Enter an image description that doesn't exceed a 1000 charcter limit.\n input: ")
            image_size_code=input("""Press the number corresponding to the listed image dimensions to choose the respective image dimension.
                                \n256x256: 1
                                \n512x512: 2
                                \n1024x1024: 3
                                """)
            return prompt, image_size_code
        elif con==1:
            prompt=input("Enter an image description that doesn't exceed a 1000 charcter limit.\n input: ")
            return prompt
        elif con==2:
            image_size_code=input("""Press the number corresponding to the listed image dimensions to choose the respective image dimension.
                                \n256x256: 1
                                \n512x512: 2
                                \n1024x1024: 3
                                \n input: """)
            return image_size_code
                                    
    except Exception as error:
        print("Error: {}\n Please try again".format(error))


def check_prompt(user_prompt: str):

    """
    Validates the user prompt for image description.

    Parameters:
        user_prompt (str): The user input for image description.

    Returns:
        str or bool: If the input is valid, returns the user prompt. 
                     If the input is "STOP", returns False to indicate stopping.
                     Otherwise, prompts the user for a new description and recursively calls itself.
                     If any exception occurs during execution, returns False.
    
    Raises:
        None
    """

    try:
        if user_prompt=="STOP":
            return False
        length=len(user_prompt)
        if length==0:
            print("Image description cannot be empty. Please enter a new description")
            user_prompt=accept_prompt(con=1)
            user_prompt=check_prompt(user_prompt)
            return user_prompt
        elif length>1000:
            print(r"length of current image description: ",length)
            print("Image description cannot exceed 1000 characters. Please enter a new description")
            user_prompt=accept_prompt(con=1)
            user_prompt=check_prompt(user_prompt)
            return user_prompt
        else:
            return user_prompt
    except Exception as error:
        print("Error: {}\n Please try again".format(error))
        return False


def check_image_size(size_code: str):
    
    """
    Checks and converts the user input for image size code to corresponding image dimensions.

    Parameters:
        size_code (str): The user input representing the image size code.

    Returns:
        str: The image dimensions corresponding to the provided size code.

    Raises:
        None
    """
    
    match size_code:
        case "1":
            image_size="256x256"
        case "2":
            image_size="512x512"
        case "3":
            image_size="1024x1024"
        case _:
            print("Invalid input for image dimension, please try again")
            size_code=accept_prompt(con=2)
            image_size=check_image_size(size_code)

    return image_size


def get_image(client, user_prompt, image_size):

    """
    Retrieves an image from the OpenAI API based on the provided user prompt and image size.

    Parameters:
        client: The OpenAI client object for making API requests.
        user_prompt (str): The user-provided prompt for generating the image.
        image_size (str): The desired size of the image.

    Returns:
        str: The URL of the generated image.

    Raises:
        Any exceptions that occur during the API request are raised.
    """

    response = client.images.generate(model="dall-e-2", prompt=user_prompt, size=image_size, quality="standard",n=1)
    image_url = response.data[0].url
    return image_url



def dis_image(url):

    """
    Displays an image from the provided URL.

    Parameters:
        url (str): The URL of the image to be displayed.

    Returns:
        PIL.Image.Image or bool: The opened image object if successful, False otherwise.

    Raises:
        Any exceptions that occur during the execution of the function are caught and printed.
    """
    
    try:
        # Fetch the image from the URL
        response = requests.get(url)
        # Check if the request was successful
        if response.status_code == 200:
            # Open the image
            image = Image.open(BytesIO(response.content))
            # Display the image
            image.show()
            return image
        else:
            print("Failed to retrieve the image")
            return False
    except Exception as error:
            print("Error: {}\n Please try again".format(error))
            return False


def get_edit(client, image, image_size, prompt, mask):

    """
    Generates an edited version of the provided image using the OpenAI API.

    Parameters:
        client: The OpenAI client object for making API requests.
        image (PIL.Image.Image): The image object to be edited.
        image_size (str): The desired size of the edited image.
        prompt (str): The prompt to guide the image editing process.
        mask (bytes): The mask for controlling the editing effect.

    Returns:
        str or bool: The URL of the edited image if successful, False otherwise.

    Raises:
        Any exceptions that occur during the API request or image processing are caught and printed.
    """
    
    try:
        byte_array = BytesIO()
        image.save(byte_array, format=image.format)
        byte_array = byte_array.getvalue()
        
        edit_response = client.images.edit(image=byte_array, mask=mask, prompt=prompt,  n=1,size=image_size, response_format="url")
        return edit_response.data[0].url
    except Exception as error:
            print("Error: {}\n Please try again".format(error))
            return False


def create_mask(image, image_size):

    """
    Creates a transparent mask image with the specified dimensions.

    Parameters:
        image: The original image object (not used in the mask creation).
        image_size (str): The dimensions of the mask image in the format "widthxheight".

    Returns:
        bytes or bool: The bytes-like object representing the mask image if successful, False otherwise.

    Raises:
        Any exceptions that occur during the creation of the mask image are caught and printed.
    """

    try:
        dimensions = image_size.split('x')
        dimension = int(dimensions[0])
        mask = Image.new("RGBA", (dimension, dimension), (0, 0, 0, 1))  # create an opaque image mask
        
        
        for x in range(dimension):
            for y in range(dimension): 
                alpha = 0
                mask.putpixel((x, y), (0, 0, 0, alpha))
        byte_array = BytesIO()
        mask.save(byte_array, format='PNG')
        byte_array = byte_array.getvalue()
        return byte_array
    except Exception as error:
            print("Error: {}\n Please try again".format(error))
            return False



def edit_image_loop(client, image, image_size):

    """
    Allows the user to iteratively edit an image until satisfaction or until 'STOP' is entered.

    Parameters:
        client: The OpenAI client object for making API requests.
        image: The original image object to be edited.
        image_size (str): The desired size of the edited image.

    Returns:
        bool: False if the user chooses to stop editing, True otherwise.

    Raises:
        None
    """

    choice=input("""Now that the image is displayed, enter your prompt to edit the image.
                    \nOtherwise, if you are satisfied with the result, enter 'STOP' to exit.""")

    if choice=="STOP":
        print("Exiting...")
        return False

    else:
        mask=create_mask(image, image_size)
        edited_url=get_edit(client, image, image_size, choice, mask)
        edited_image=dis_image(edited_url)
        loop_res=edit_image_loop(client, edited_image, image_size)
        return loop_res
        

def main(client):

    """
    Main function to interactively generate and edit images.

    Parameters:
        client: The OpenAI client object for making API requests.

    Returns:
        None

    Raises:
        None
    """
    user_prompt, size_code=accept_prompt()
    user_prompt=check_prompt(user_prompt)
    if not user_prompt:
        print("Exiting...")
        return
    image_size=check_image_size(size_code)
    url=get_image(client, user_prompt, image_size)
    image=dis_image(url)
    loop_res=edit_image_loop(client, image, image_size)
    return

if __name__=="__main__":

    client = OpenAI(api_key="your openai api key goes here")
    main(client)
    



