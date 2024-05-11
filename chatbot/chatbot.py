# import the OpenAI Python library for calling the OpenAI API
from openai import OpenAI
from config.settings import OPENAI_API_KEY, OPENAI_MODEL
from vectorization.encoder import vectorize_string
from database.pinecone_manager import PineconeManager

chatbot = OpenAI(api_key=OPENAI_API_KEY)

# messages = [
#     {
#         "role": "system",
#         "content": "You are a helpful assistant who helps Princeton students select courses for the upcoming semester.",
#     },
#     {"role": "user", "content": "Knock knock."},
#     {"role": "assistant", "content": "Who's there?"},
#     {"role": "user", "content": "Orange."},
# ]


def get_gpt_response(chatbot, messages):
    """Interact with OpenAI's GPT to process the user query."""
    response = chatbot.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0,
    )

    return response.choices[0].message.content


def generate_hypothetical_description(student_input):
    messages = [
        {
            "role": "system",
            "content": "You are an assistant that produces course descriptions given the interests of students. For example, if a student says they are interested in topic X, your job is to generate a 100-200 word description for a hypothetical course that discusses one or all of these topics. Note that not all of the topics stated by the student must be covered in the course, so don’t feel like you need to use all of them. For instance, if a student says they are interested in the modern history of drugs, you could output ‘The production and distribution of narcotics is one of the world's largest industries, and has been a quintessential example of the globalized economy since at least the 19th century. This course follows how the Latin American drug trade works and how it is understood, both conceptually and spatially, from source to user. Therefore, the course addresses areas of drug production; the dynamics and experiences of drug trafficking, including the origins of narcotics illegalization and state efforts to curtail the drug trade; and finally, the consumption of drugs and the practice's policing by state authorities.’ Please only output the description and no surrounding text. ",
        },
        {"role": "user", "content": student_input},
    ]
    response = chatbot.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=1,
    )
    return response.choices[0].message.content

    # async def chatbot():
    print(
        "Hi! I am here to help you find interesting courses for next semester. What are you interested in?"
    )
    while True:
        user_input = input("> ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Use GPT to understand and generate a response based on the user's input
        processed_input = get_gpt_response(user_input)
        print("Let me check that for you...")

        # Assume process_query converts the GPT output to a query vector
        query_vector = vectorize_descriptions(processed_input)

        # Fetch relevant courses (using a mock PineconeManager here)
        pinecone_manager = PineconeManager()
        relevant_courses = pinecone_manager.query(query_vector)

        if relevant_courses:
            print("Here are some courses that might interest you:")
            for course in relevant_courses["matches"]:
                print(
                    f"- {course['metadata']['titles'][0]}: {course['metadata']['description']}"
                )
        else:
            print(
                "I couldn't find any courses matching your description. Could you please specify a bit more?"
            )


def get_related_courses(description):
    query_vector = vectorize_string(description).tolist()
    # Fetch relevant courses (using a mock PineconeManager here)
    pinecone_manager = PineconeManager()
    relevant_courses = pinecone_manager.query(query_vector, top_k=15)

    if relevant_courses:
        print("Here are some courses that might interest you:")
        # print(relevant_courses["matches"])
        # for course in relevant_courses["matches"]:
        #     print(
        #         f"- {course['metadata']['title']}: {course['metadata']['description']}"
        #     )
        return relevant_courses
    else:
        print(
            "I couldn't find any courses matching your description. Could you please specify a bit more?"
        )


def summarize_related_courses(relevant_courses, student_input):
    relevant_courses_formatted = ""

    for course in relevant_courses["matches"]:
        # Append each line to the output_string
        relevant_courses_formatted += (
            f"- {course['metadata']['title']}: {course['metadata']['description']}\n"
        )

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant who helps Princeton students select courses for the upcoming semester.",
        },
        {"role": "user", "content": student_input},
        {
            "role": "system",
            "content": f"Here are some courses that are potentially related to the student's input. Use this information to respond to the student and suggest some courses. Note that the course information that follows is in the format of - COURSE_NAME: COURSE_DESCRIPTION. Here is the course information: {relevant_courses_formatted}",
        },
    ]

    response = chatbot.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=1,
    )

    return response.choices[0].message.content


def test_description():
    chatbot = OpenAI(api_key=OPENAI_API_KEY)
    student_input = "I'm a STEM major, but I'm super into music and I want to take an electronic music class that doesn't shy away from the more technical aspects of production and composition."

    description = generate_hypothetical_description(chatbot, student_input)
    print(description)
