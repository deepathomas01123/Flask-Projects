# importing the necessary packages
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import boto3
import requests
import json
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def login_page():
    return render_template('login.html')


# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    #  Lambda login API url
    lambda_login_url = "https://np8g39y3v5.execute-api.us-east-1.amazonaws.com/beta/user_login_lambda"

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Prepare the data payload in the format expected by the Lambda function
        data = {email: password}

        try:
            # Make the request to the API Gateway
            response = requests.post(lambda_login_url, json=data)
            response_data = json.loads(response.json()['body'])
            status_code = response.json()['statusCode']
            # check the status code
            if status_code == 200:
                session['user_name'] = response_data['user_name']  # Store user_name in session if needed
                session['user_email'] = email  # Store user email in session
                return redirect(url_for('success'))  # Return to the main page upon successful login
            else:
                flash(response_data['message'])
                return render_template('login.html')

        except requests.RequestException as e:
            # Handle connection errors
            print(f"Request failed: {e}")
            flash('Failed to connect to authentication service. Please try again.')
            return render_template('login.html')
    else:
        # Show the login form for GET requests
        return render_template('login.html')


# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Lambda register API url
    lambda_api_url = 'https://oisqyvk2c7.execute-api.us-east-1.amazonaws.com/beta/user_registration_lambda'

    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        # Prepare data for the API request
        data = {
            'email': email,
            'user_name': username,
            'password': password
        }

        try:
            # Make a POST request to the Lambda function
            response = requests.post(lambda_api_url, json=data)
            response_data = response.json()
            status_code = response_data['statusCode']
            message = json.loads(response_data['body'])['message']

            # Check the status code
            if status_code == 200:
                flash(message)
                return redirect(url_for('login'))
            elif status_code == 400:
                flash(message)
            else:
                flash('An error occurred. Please try again.')
        except requests.exceptions.RequestException as e:

            print(e)
            flash('An error occurred. Please try again.')
    return render_template('register.html')


# Remove subscribed music
@app.route('/remove_subscription', methods=['POST'])
def remove_subscription():
    # Lambda remove subscription api url
    lambda_remove_subscription_url = 'https://4n9gs4g3v9.execute-api.us-east-1.amazonaws.com/beta/user_removesubscription_lambda'

    user_email = request.form['email']
    title = request.form['title']
    # Prepare data for the API request
    data = {
        'email': user_email,
        'title': title,
    }
    try:
        response = requests.post(lambda_remove_subscription_url, json=data)
        response_data = response.json()
        status_code = response_data['statusCode']
        message = json.loads(response_data['body'])['message']
        # Check the status code
        if status_code == 200:
            flash(message, 'success')
        else:
            # Handle non-200 responses
            message = 'Failed to remove subscription.'
            flash(message, 'error')
    except requests.exceptions.RequestException as e:
        print(e)
        flash('An error occurred. Please try again.')
    return redirect(url_for('success'))


# Main Page
@app.route('/success', methods=['GET', 'POST'])
def success():
    # Lambda API url
    lambda_query1_url = 'https://l9ir44fw9l.execute-api.us-east-1.amazonaws.com/beta/user_query1_lambda'
    lambda_query2_url = 'https://aytomlwx2l.execute-api.us-east-1.amazonaws.com/beta/user_query2_lambda'

    user_name = session.get('user_name', 'Guest')  # Guest is the default name if user not found
    user_email = session.get('user_email')

    queried_items = []  # Default to no items
    if request.method == 'POST':
        title = request.form.get('title').lower().strip()
        artist = request.form.get('artist').lower().strip()
        year = request.form.get('year').strip()

        # Build a dictionary of filter conditions
        filter_conditions = {
            'title': title,
            'artist': artist,
            'year': year
        }

        # Send this dictionary to the Lambda function to perform the query function
        response = requests.post(lambda_query2_url, json=filter_conditions)
        response_data = response.json()
        queried_items = response_data['body']
        print(queried_items)
        if not queried_items:
            flash('No result is retrieved. Please query again', 'info')

    # Set the headers including the user email
    headers = {
        'Content-Type': 'application/json',
        'X-User-Email': user_email
    }
    # Construct the request body in the format Lambda expects
    lambda_request_body = {
        "headers": headers,
    }
    # Make the POST request to the Lambda function via API Gateway
    response = requests.post(lambda_query1_url, json=lambda_request_body)
    response_data = response.json()
    subscriptions = response_data['body']
    return render_template('success.html', user_name=user_name, subscriptions=subscriptions, items=queried_items)


@app.route('/subscribe', methods=['POST'])
def subscribe():
    # Lambda API url
    lambda_subscription_url = 'https://dt1ogrk23j.execute-api.us-east-1.amazonaws.com/beta/user_subscription_lambda'

    # Get user_email from the session
    user_email = session.get('user_email')
    if not user_email:
        flash('You must be logged in to subscribe.', 'warning')
        return redirect(url_for('login'))

    # Prepare data for the API call
    subscription_data = {
        'title': request.form['title'],
        'artist': request.form['artist'],
        'year': request.form['year']
    }

    # Convert subscription_data to a JSON string
    subscription_data_json = json.dumps(subscription_data)

    # Set the headers including the user email
    headers = {
        'Content-Type': 'application/json',
        'X-User-Email': user_email
    }

    # Construct the request body in the format Lambda expects
    lambda_request_body = {
        "headers": headers,
        "body": subscription_data_json
    }

    # Make the POST request to the Lambda function via API Gateway
    response = requests.post(lambda_subscription_url, json=lambda_request_body)
    response_data = response.json()
    status_code = response_data['statusCode']

    # Check the response from the Lambda function
    if status_code == 200:
        response_message = response.json()['body'].strip('"')  # Strip extra quotes if present
        flash(response_message, 'success')
    else:
        flash('Failed to subscribe. Please try again.', 'error')

    return redirect(url_for('success'))


@app.route('/logout')
def logout():
    # Remove user information from session
    session.pop('user_name', None)
    session.pop('user_email', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
