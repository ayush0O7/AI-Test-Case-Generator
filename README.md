# APP MADE USING GPT-3.5 OPEN AI APIs

This is an application that generates detailed test cases given the requirements of an application. 
It can either be given the URL containing the requirements of an application or the requirements in plain text.

It uses the [Flask](https://flask.palletsprojects.com/en/2.0.x/) web framework.

## Setup

1. If you don’t have Python installed, [install it from here](https://www.python.org/downloads/)

2. Clone this repository

3. Navigate into the project directory

   ```bash
   $ cd openai-quickstart-python
   ```

4. Create a new virtual environment and activate it.

   ```bash
   $ python -m venv venv
   $ . venv/bin/activate
   ```

5. Install the requirements

   ```bash
   $ pip install -r requirements.txt
   ```

6. Make a copy of the example environment variables file

   ```bash
   $ cp .env.example .env
   ```

7. Add your [API key](https://beta.openai.com/account/api-keys) to the newly created `.env` file

8. Run the app

   ```bash
   $ flask run
   ```

You should now be able to access the app at [http://localhost:5005]
