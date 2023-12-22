from flask import Flask
from flask import render_template
from flask import Response, request, jsonify
app = Flask(__name__)

#for gpt
import os
import openai
import PyPDF2

import secrets
openai.api_key = 'ENTER YOUR KEY HERE'



#for dalle
import json
from base64 import b64decode
from pathlib import Path

headline_data = {
    "name":"",
    "rec-name":"",
    "known":"",
    "request":"",
    "reason":"",
    "relationship":"",
    "generations":"",
    "cache":[],
    "explanation":"",
    "you": "",
    "recu": "",
    "ask": "",
    "resume": "",
    "error": False
}

@app.route('/write_known_email', methods = ['GET', 'POST'])
def write_known_email():
    global headline_data
    data = request.get_json()

    headline_data["request"] = data["request"]
    headline_data["reason"] = data["reason"]
    headline_data["relationship"] = data["relationship"]

    name = headline_data["name"]
    rec = headline_data["rec-name"]
    reason = headline_data["reason"]
    relationship = headline_data["relationship"]

    if headline_data["request"] == "extension":
        prompt = f"You are a student named {name} taking a class taught by {rec}. Write her an email asking for an extension on an assignment because {reason}. Do not include a subject line in your output. Do not make up any information and only use these details: {relationship}"
    elif headline_data["request"] == "absence":
        prompt = f"You are a student named {name} taking a class taught by {rec}. Write her an email letting her know you are missing a class meeting because {reason}. Do not include a subject line in your outpur. Do not make up any information and only use these details: {relationship}"
    else:
        prompt = f"Your are a student named {name} and you know {rec}. Write her an email saying that {reason}. Do not include a subject line in your output. Do not make up any information and only use these details: {relationship}"

    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256)["choices"][0]["text"]
    headline_data["generations"] = response
    email = headline_data["generations"]

    if headline_data["request"] == "extension":
        feedback_prompt = f"You are a professor evaluating an email from a student in your class asking for an extension. Provide feedback, including calling out specific sections, on the effectivness of the email. Do not address the student or sign-off with your name. The email is here: {email}"
    elif headline_data["request"] == "absence":
        feedback_prompt = f"You are a professor evaluating an email from a student in your class letting you know they will be missing class. Provide feedback, including calling out specific sections, on the effectivness of the email.Do not address the student or sign-off with your name. The email is here: {email}"
    else:
        feedback_prompt = f"You are a professor evaluating an email from a student. The student reached out because {reason}. Provide feedback, including calling out specific sections, on the effectivness of the email. Do not address the student or sign-off with your name. The email is here: {email}"


    prompt = f"Write a subject line for the following email and output only the text of the subject line, without any title indicating it is a subject line or quotes around it: {email}"
    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256)["choices"][0]["text"]
    headline_data["subject"] = response

    response = openai.Completion.create(engine="text-davinci-003", prompt=feedback_prompt, max_tokens=256)["choices"][0]["text"]
    headline_data["explanation"] = response

    print(headline_data["subject"])
    print(headline_data["explanation"])

    return jsonify(headline_data)

@app.route('/write_unknown_email', methods = ['GET', 'POST'])
def write_unknown_email():
    global headline_data
    data = request.get_json()

    headline_data["you"] = data["you"]
    headline_data["reason"] = data["reason"]
    headline_data["recu"] = data["recu"]
    headline_data["ask"] = data["ask"]
    headline_data["resume"] = data["resume"]
    headline_data["relationship"] = data["relationship"]

    rec = headline_data["rec-name"]
    you = headline_data["you"]
    reason = headline_data["reason"]
    uni = headline_data["recu"]
    relationship = headline_data["relationship"]

    
    try:
        file = open(headline_data["resume"],'rb')
        fileReader = PyPDF2.PdfFileReader(file)
        pageObj = fileReader.getPage(0)
        text = pageObj.extractText()
        headline_data["error"] = False
    except:
        headline_data["error"] = True

    prompt = f"Write a few paragraphs summarizing the research interests and most recent work of {rec} at {uni}. Do not include any information that you are not 100% confident about."
    professor_info = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256)["choices"][0]["text"]

    if headline_data["error"]:
        if headline_data["ask"] == "coffeechat":
            prompt = f"You are a student with the following background: {you}. Write an email to {rec} asking to schedule a coffee chat because {reason}. Do not include a subject line. Do not make up any information and only use these details: {relationship}. A summary of {rec} work is here: {professor_info}"
        elif headline_data["ask"] == "resources":
            prompt = f"You are a student with the following background: {you}. Write an email to {rec} asking for learning and research resources because {reason}. Do not include a subject line. Do not make up any information and only use these details: {relationship}.  A summary of {rec} work is here: {professor_info}"
        else:
            prompt = f"You are a student with the following background: {you}. Write an email to {rec} because {reason}. Do not include a subject line. Do not make up any information and only use these details: {relationship}.  A summary of {rec} work is here: {professor_info}"
    else:
        if headline_data["ask"] == "coffeechat":
            prompt = f"You are a student with the following background: {you}. Write an email to {rec} asking to schedule a coffee chat because {reason}. Do not include a subject line. Do not make up any information and only use these details: {relationship}.  A summary of {rec} work is here: {professor_info}.  Also include details from your resume: {text}"
        elif headline_data["ask"] == "resources":
            prompt = f"You are a student with the following background: {you}. Write an email to {rec} asking for learning and research resources because {reason}. Do not include a subject line. Do not make up any information and only use these details: {relationship}.  A summary of {rec} work is here: {professor_info}. Also include details from your resume: {text}"
        else:
            prompt = f"You are a student with the following background: {you}. Write an email to {rec} because {reason}. Do not include a subject line. Do not make up any information and only use these details: {relationship}. A summary of {rec} work is here: {professor_info}. Also include details from your resume: {text}"
    
    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256)["choices"][0]["text"]
    headline_data["generations"] = response
    email = headline_data["generations"]

    if headline_data["ask"] == "coffeechat":
        feedback_prompt = f"You are a professor who is evaluating an email from a student asking for a coffee chat. Provide feedback, including calling out specific sections, on the effectivness of the email. Check particularly if the student makes a compelling argument as to why they are interested in your work. Do not address the student or sign-off with your name. The email is here: {email}"
    elif headline_data["ask"] == "resources":
        feedback_prompt = f"You are a professor who is evaluating an email from a student asking for learning and research resources. Provide feedback, including calling out specific sections, on the effectivness of the email. Check particularly if the student makes a compelling argument as to why they are interested in your work. Do not address the student or sign-off with your name. The email is here: {email}"
    else:
        feedback_prompt = f"You are a professor evaluating an email from a student. Provide feedback, including calling out specific sections, on the effectivness of the email. Check particularly if the student makes a compelling argument as to why they are interested in your work. Do not address the student or sign-off with your name. The email is here: {email}"

    prompt = f"Write a subject line for the following email and output only the text of the subject line, without any title indicating it is a subject line or quotes around it: {email}"
    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256)["choices"][0]["text"]
    headline_data["subject"] = response

    response = openai.Completion.create(engine="text-davinci-003", prompt=feedback_prompt, max_tokens=256)["choices"][0]["text"]
    headline_data["explanation"] = response

    return jsonify(headline_data)

@app.route('/make_adjustments', methods=['GET', 'POST'])
def make_adjustments():
    global headline_data
    data = request.get_json()   

    change = data["change"]
    email = headline_data["generations"]
    prompt = f"You have been given the following instructions to adjust an email: {change}. Rewrite this email as per the instructions: {email}"
    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256)["choices"][0]["text"]
    headline_data["generations"] = response

    print(response)

    return jsonify(headline_data)

@app.route('/submit_headline', methods=['GET', 'POST'])
def submit_headline():
    global headline_data
    data = request.get_json()   

    headline_data["headline"] = data["headline"]
    headline_data["summary"] = data["summary"]
    headline_data["content"] = data["content"]
    headline_data["tone"] = data["tone"]

    headline_data["generations"] = generate_email(headline_data["headline"], headline_data["summary"], headline_data["content"], headline_data["tone"])
    if headline_data["generations"] not in headline_data["cache"]: headline_data["cache"].append(headline_data["generations"])

    #send back the WHOLE array of data, so the client can redisplay it
    return jsonify(headline_data)

@app.route('/save_first_submission_info', methods=['GET', 'POST'])
def save_first_submission_info():
    global headline_data
    data = request.get_json() 

    headline_data["name"] = data["name"]
    headline_data["rec-name"] = data["rec"]
    headline_data["known"] = data["known"]

    #send back the WHOLE array of data, so the client can redisplay it
    return jsonify(headline_data)

@app.route('/user_adjustment', methods=['GET', 'POST'])
def user_adjustment():
    data = request.get_json()

    if headline_data["generations"] not in headline_data["cache"]: headline_data["cache"].append(headline_data["generations"])
    headline_data["change"] = data["change"]
    change = headline_data["change"]
    email = headline_data["generations"]
    prompt = f"Consider the following email in quotes: \"{email}\". Change it as per the following instructions in quotes: \"{change}\"."
    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256)["choices"][0]["text"]
    headline_data["generations"] = response

    return jsonify(headline_data)

@app.route('/give_feedback', methods=['GET', 'POST'])
def give_feedback():

    recipient = headline_data["headline"]
    relation = headline_data["new"]
    message = headline_data["last"]
    reason = headline_data["lastlast"]
    email = headline_data["generations"]

    prompt = f"Provide constructive criticism in list format about this email, written to {recipient} from one of her students: {email}"
    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256)["choices"][0]["text"]
    headline_data["feedback"] = response

    return jsonify(headline_data)

@app.route('/undo_sauce', methods=['GET', 'POST'])
def undo_sauce():
    print("undo")
    if headline_data["generations"] not in headline_data["cache"]: headline_data["cache"].append(headline_data["generations"])
    headline_data["generations"] = headline_data["cache"][-2]

    return jsonify(headline_data)

@app.route('/get_key', methods=['GET', 'POST'])
def get_key():
    global headline_data
    data = request.get_json()

    headline_data = data
    return jsonify(headline_data)

@app.route('/first_submission', methods=['GET', 'POST'])
def first_submission():
    global headline_data
    data = request.get_json()   

    headline_data["headline"] = data["headline"]

    #send back the WHOLE array of data, so the client can redisplay it
    return jsonify(headline_data)

@app.route('/second_submission', methods=['GET', 'POST'])
def second_submission():
    global headline_data
    data = request.get_json()   

    print('in the sub')

    headline_data["new"] = data["new"]
    headline_data["last"] = data["last"]
    headline_data["lastlast"] = data["lastlast"]

    headline_data["generations"] = generate_email_new_(headline_data)
    if headline_data["generations"] not in headline_data["cache"]: headline_data["cache"].append(headline_data["generations"])

    # headline_data["generations"] = "Subject: Columbia master’s student interested in collaborating on research \nDear Dr. Chilton,\nMy name is Karthik Sreedhar and I am a computer science and journalism master’s student at Columbia University. I am reaching out because I am interested in discussing the possibility of collaborating on research exploring human-computer interaction and generative AI. I am fascinated by the ways in which the research projects at the Computational Design Lab utilize technology to make individuals’ everyday lives easier. \nMy prior research has overlap with your work; in the past, I worked with Professor Armando Fox on a human-computer interaction study that aimed to improve computer science instruction and evaluation of adherence to agile methodology by student teams. I am eager to see how I could apply the same techniques to contribute to building user-focused technologies that use generative AI, especially in the context of journalism, as I noticed you had worked on several relevant projects.\nI would love to have a brief conversation in the next week to learn more about your research and discuss how my project experience and research knowledge could be beneficial in advancing your academic work.\nSincerely,\nKarthik Sreedhar"

    #send back the WHOLE array of data, so the client can redisplay it
    return jsonify(headline_data)

def generate_email_new_(headline_data):
    recipient = headline_data["headline"]
    relation = headline_data["new"]
    message = headline_data["last"]
    reason = headline_data["lastlast"]

    prompt = f"Write a short email, with a subject line, for me addressed to {recipient}, whom I know because {relation}. I am writing because {message}. The reason for this request is {reason}."
    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256)["choices"][0]["text"]

    return response


def generate_email_new_new(headline_data):
    recipient = headline_data["headline"]
    intro = headline_data["new"]
    motivation = headline_data["content"]
    priorExp = headline_data["tone"]
    profExp = headline_data["subject"]
    ask = headline_data["last"]

    # website = f"Summarize this website: {profExp}"
    # website = f"What does {recipient} work on? Only include information you are confident about - otherwise you will be fired."
    # summary = openai.Completion.create(engine="text-davinci-003", prompt=website, max_tokens=256)["choices"][0]["text"]

    summary = "Lydia Chilton’s area of study is human-computer interaction with a focus on computational design, including viewing the design process from a computational standpoint. Two current projects are constructing visual metaphors for creative ads and using computational tools to write humor and news satire."

    # print(summary)

    mywork = f"Can you summarize this role I have had in the past for me? Here is the role with the title and company in the first line, and the description in bullet points: {priorExp}"
    myworksum = openai.Completion.create(engine="text-davinci-003", prompt=mywork, max_tokens=256)["choices"][0]["text"]

    print(myworksum)

    connection_ = f"Make a connection between {recipient} and myself. Here is information about {recipient}: {summary}. Here is information about myself: {myworksum}"
    connection__ = openai.Completion.create(engine="text-davinci-003", prompt=connection_, max_tokens=256)["choices"][0]["text"]

    print(connection__)

    prompt = f"Help me write a cold-email to {recipient}. I am reaching out because {motivation}. The connection between my own work and {recipient} is here: {connection__}. Please reference at least one specific line of research of {recipient} in the email. My specific ask is {ask}. Use the next sentence as an introduction: {intro}."
    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256)["choices"][0]["text"]

    print(response)

    return response

def parse_keywords_from_gpt_response(keyword_response):    
    keyword_list = keyword_response.splitlines()
    new_keyword_list = []
    for i, item in enumerate(keyword_list):
        item = item.strip()
        if item != "":
            item = item[item.index(".") + 1:]
            item = item.strip()
            new_keyword_list.append(item)
    return new_keyword_list
    
def generate_email(headline, summary, content, tone):
    prompt =  f"Given the context that {headline}, write an {tone} email to {summary} conveying that {content}. Do not include any inormation beyond what is provided in this prompt. \
    Include a subject line at the beginning of the email and print it out on a separate line from the rest of the email."
    print(prompt)
    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256)["choices"][0]["text"]
    print(response)

    return response


@app.route('/')
def home():
    # you can pass in an existing article or a blank one.
    return render_template('home.html', data=headline_data)   


if __name__ == '__main__':
    # app.run(debug = True, port = 4000)    
    app.run(debug = True)




