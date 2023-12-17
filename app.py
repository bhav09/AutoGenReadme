from git import Repo
import streamlit as st
import re
from bardapi import Bard
import json
import os
from tree_maker import tree


# Function to generate the output
def generate_response(prompt):
    bard = Bard(token=token)
    response = bard.get_answer(prompt)['content']
    return response


# Function to receive user queries
def get_text(key, text, height):
    input_text = st.text_area(text, "", key=key, height=height)
    return input_text


# Function to extract imports from Python files
def extract_imports(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Use a regular expression to find import statements
    import_regex = re.compile(r'^\s*import\s+[\w\s,]+\s*$|^\s*from\s+[\w.]+\s+import\s+[\w\s*,]+\s*$',
                              re.MULTILINE)

    # Find all matches in the file content
    import_matches = import_regex.findall(content)

    # Return the list of import statements
    return import_matches


# Function to find python files
def find_python_files(directory):
    python_files = []

    # requirements_found: [requirements.txt found or not, path]
    requirements_found = [False, None]

    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file has a .py extension
            if file.startswith("requirements.txt"):
                requirements_found[0] = True
                requirements_found[1] = os.path.join(root, file)

            if file.endswith(".py"):
                # Get the full path of the Python file
                file_path = os.path.join(root, file)
                python_files.append(file_path)

    return python_files, requirements_found


# Function to generate readme file
def generate_readme():
    global response

    code_file = ''
    all_imports = ''
    if deep_read:
        prompt = f"""
        Write an interesting README file for a github repository: "{clone_to}". 
        It consists: {repo_context}
        
        Instructions:
        1. Be concise and short in response
        2. The code is written in python. Share the dependencies to install etc.
        3. The readme file should be well formatted.
        4. Include appropriate emojis, heading tags, bullets etc. wherever necessary.
        5. Mention that directory tree can be understood by referring the file "tree.txt"
        6. Do not include any redundant piece of response.
        7. Read the below code for context: \n {code_file}
        """
    else:
        python_files, requirements_found = find_python_files(clone_to)
        if not requirements_found[0]:
            all_imports = []
            for file in python_files:
                imports = extract_imports(file)
                imports = ''.join(imports)
                all_imports.append(imports)
        else:
            all_imports = open(requirements_found[1], 'r').read()

        prompt = f"""
        Write an interesting README file for a github repository: "{clone_to}". 
        It consists: {repo_context}
        
        Instructions:
        1. Be concise and short in response
        2. The code is written in python. Share the dependencies to install etc.
        3. The readme file should be well formatted.
        4. Always Include appropriate emojis, heading tags, bullets etc. wherever necessary.
        5. Mention that directory tree can be understood by referring the file "tree.txt"
        6. Do not include any redundant piece of response.
        7. Read the below imports for context: \n {all_imports}
        """

    print(all_imports)
    response = generate_response(prompt)
    # return response


# Function to write Readme file
def download_readme():
    readme_file = open(f'{clone_to}/README.md', 'w')
    readme_file.write(response)


# Function to clone the repo
def git_clone(clone_from, clone_to):
    Repo.clone_from(clone_from, clone_to)


# Function to push the repo
def git_push():
    message = 'Updated via AutoGenREADME'

    try:
        repo = Repo(clone_to)
        print('Files Adding')
        repo.index.add(['README.md', 'tree.txt'])
        repo.git.add(update=True)
        repo.index.commit(message)
        print('Files Added!')
        origin = repo.remote(name='origin')
        origin.push()
    except Exception as e:
        print(e)
        print('Some error occured while pushing the code')


if __name__ == '__main__':

    with open('credentials.json', 'r') as f:
        file = json.load(f)
        token = file['bard_token']

    response = ''
    # Title of the streamlit app
    st.title('README Generator!')
    deep_read = False
    # https://s5.gifyu.com/images/Si8BC.gif
    changes = '''
    <style>
    [data-testid = "stAppViewContainer"]
        {
        background-image:url('https://s5.gifyu.com/images/Si8OM.gif');
        background-size:cover;
        }
        
        div.esravye2 > iframe {
            background-color: transparent;
        }
    </style>
    '''
    st.markdown(changes, unsafe_allow_html=True)

    # Accepting user input
    clone_from = st.text_input("**Paste your URL here 👇🏻**", '', key='input')
    clone_to = clone_from.split('/')[-1][:-4]
    if clone_from:
        if not os.path.exists(clone_to):
            git_clone(clone_from, clone_to)
        st.write("✅ Repo Cloned!")
        tree(clone_to)

        repo_context = get_text('repo_context', 'Context', 100)
        col1, col2 = st.columns([1, 2.5])
        gen_readme = col1.button('Generate README')
        if gen_readme:
            # print(repo_context)
            generate_readme()
        deep_read = col2.checkbox('Deep Read')

        st.markdown(
            """
            <style>
                .stCheckbox {
                    margin-top: 5px;
                }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.write("✅ README Generated!")

        col1, col2 = st.columns([1, 2.5])
        push_button = col1.button('Push Repo', key='push_repo')
        download_button = col2.button('Download README', on_click=download_readme, key='download_readme')
        if push_button:
            git_push()
            st.write("✅ Repo Pushed!")
