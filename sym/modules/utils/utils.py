import os
import jinja2
import base64
import time
from sym.modules.db.models import Token
import requests

from io import BytesIO
import boto3

class InvalidAuth(Exception):
    pass


def authenticate_user(session, request):
    headers = request.headers
    if "X-Api-Key" not in headers:
        raise InvalidAuth("X-Api-Key not in headers")
    token  = headers["X-Api-Key"]
    now = time.time()
    
    token_obj = session.query(Token) \
        .filter(Token.token==token, Token.expires_on>=now) \
        .first()
    
    if token_obj is None:
        raise InvalidAuth("No token found")
    u = token_obj.get_user(session)
    return u


def render_template(template_name, context, template_prefix="chalicelib/templates/"):
    template_path = template_prefix+template_name
    path, filename = os.path.split(template_path)
    return jinja2.Environment(loader=jinja2.FileSystemLoader(path or "./")).get_template(filename).render(context)

def render_resource(resource_name, context={}, resource_prefix="chalicelib/static/"):
    resource_path = resource_prefix+resource_name
    path, filename = os.path.split(resource_path)
    return jinja2.Environment(loader=jinja2.FileSystemLoader(path or "./")).get_template(filename).render(context)


def static_image(resource_name, resource_prefix="chalicelib/static/images/"):
    resource_path = resource_prefix+resource_name
    with open(resource_path, "rb") as image_file:
        bytes = image_file.read()
    return bytes


def render_from_frontend_bucket(resource_name, 
        bucket_url="https://sym-frontend.s3.us-west-2.amazonaws.com/",
        filepath=""):
    r = requests.get(bucket_url+filepath+resource_name)
    return r.content

def redirect_to_bucket(
        resource_name, 
        bucket_url="https://sym-public.s3.us-west-2.amazonaws.com/",
        filepath=""):
    redirect_path = bucket_url+filepath+resource_name
    return redirect_path


def redirect_to_frontend_bucket(
        resource_name, 
        bucket_url="https://sym-frontend.s3.us-west-2.amazonaws.com/",
        filepath=""):
    redirect_path = bucket_url+filepath+resource_name
    return redirect_path


def get_project_user(user, project):
    """ Given a user and a project, get the linking UserProject record"""
    for project_user in user.projects:
        if project_user.project_id == project.id:
            return project_user
    return None

def user_can_read_project(user, project):
    project_user = get_project_user(user, project)
    return project_user.can_read if project_user else False

def user_can_update_project(user, project):
    project_user = get_project_user(user, project)
    return project_user.can_update if project_user else False

def user_can_create_project(user, project):
    #note: name is a bit strange, 
    # but we mean this user can create new resources in this project
    # Like they can add a new keyword, or a new niche
    project_user = get_project_user(user, project)
    return project_user.can_create if project_user else False

def user_can_delete_project(user, project):
    project_user = get_project_user(user, project)
    return project_user.can_delete if project_user else False


def upload_image_to_s3(image_url, folder="images", bucket_name="sym-public-assets", object_name=None):
    # Download the image
    response = requests.get(image_url)
    if response.status_code != 200:
        return f"Failed to download image: Status code {response.status_code}"

    # If no object name is given, use the last part of the image URL
    if object_name is None:
        object_name = image_url.split("?")[0].split("/")[-1]
    
    #add to a folder for organization
    object_name = f"{folder}/{object_name}"

    # Create an S3 client
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    s3_client = boto3.client('s3', 
                    aws_access_key_id=AWS_ACCESS_KEY_ID, 
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    

    # Upload the image to S3
    try:
        s3_client.upload_fileobj(BytesIO(response.content), bucket_name, object_name)
    except Exception as e:
        print(f"Error uploading file to S3: {str(e)}")
        return None

    # Construct the URL of the new object in S3
    s3_url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"

    return s3_url