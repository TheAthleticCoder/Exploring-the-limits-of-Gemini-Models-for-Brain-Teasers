import numpy as np
import google.generativeai as genai
import csv
import argparse
from tqdm import tqdm

# loading the .npy file
def parse_args():
    parser = argparse.ArgumentParser(description="Generate responses using Gemini model and store in CSV file.")
    parser.add_argument('--input_file', required=True, help='Path to the input .npy file')
    parser.add_argument('--output_csv', required=True, help='Path to the output CSV file')
    return parser.parse_args()

# parse command-line arguments
args = parse_args()

# load the .npy file
file_path = args.input_file
data = np.load(file_path, allow_pickle=True)

# template
template = """
Welcome to the word-play puzzle challenge! Here, you will be presented with a question based on a word-play puzzle. It means that the question is a brain teaser where the answer violates the default meaning of the word and focuses on the letter composition of the target question.
We have given you two examples below to help you understand the puzzle challenge better.
Example 1:
Question: {}
Choices:\n{}
Correct Option: {}

Example 2:
Question: {}
Choices:\n{}
Correct Option: {}

Now, we shall be giving you the puzzle you need to solve. Remember to pay attention to the details mentioned and indicate the option number you believe is correct for the question:
Question: {}
Choices:\n{}
"""

# list to store formatted entries
formatted_data = []

# iterating through entries and format them
for entry in tqdm(data, desc="Formatting Entries", unit="entry"):
    question = entry['question']
    choices = entry['choice_list']
    #t1
    t1_question = entry['closest_train_data1']['question']
    t1_choices = entry['closest_train_data1']['choice_list']
    t1_label = entry['closest_train_data1']['label']
    t1_label += 1 #to make it 1-indexed
    t1_reason = entry['closest_train_data1']['reason']
    #t2
    t2_question = entry['closest_train_data2']['question']
    t2_choices = entry['closest_train_data2']['choice_list']
    t2_label = entry['closest_train_data2']['label']
    t2_label += 1 #to make it 1-indexed
    t2_reason = entry['closest_train_data2']['reason']
    # format the choices with options and newline characters
    formatted_choices = '\n'.join([f"Option {i}: {choice}" for i, choice in enumerate(choices, start=1)])
    formatted_t1_choices = '\n'.join([f"Option {i}: {choice}" for i, choice in enumerate(t1_choices, start=1)])
    formatted_t2_choices = '\n'.join([f"Option {i}: {choice}" for i, choice in enumerate(t2_choices, start=1)])
    # format the entry using the template
    formatted_entry = template.format(t1_question, formatted_t1_choices, t1_label, t2_question, formatted_t2_choices, t2_label, question, formatted_choices)
    # append the formatted entry to the list
    formatted_data.append(formatted_entry)

print("Phase 1 Complete\n")
# initialize the generative model
import google.generativeai as genai
genai.configure(api_key="")
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]
generation_config = {
    "temperature": 0.1,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}
model = genai.GenerativeModel(model_name="gemini-pro", generation_config=generation_config, safety_settings=safety_settings)
print("Phase 2 Complete\n")
# list to store input and output for CSV
output_data = []

# iterate through formatted data and generate responses
for i, prompt in enumerate(tqdm(formatted_data, desc="Generating Responses", unit="entry"), start=1):
    # run the gemini model on the input
    response = model.generate_content(prompt)
    # append input and output to the list
    input_output_pair = {'input': prompt, 'output': response.text}
    output_data.append(input_output_pair)

# storing the output in a CSV file
csv_file_path = args.output_csv
csv_columns = ['input', 'output']

with open(csv_file_path, 'w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
    writer.writeheader()
    for pair in output_data:
        writer.writerow(pair)

print(f"\nCSV file with input-output pairs saved at: {csv_file_path}")

