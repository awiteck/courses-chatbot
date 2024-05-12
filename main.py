import asyncio
from vectorization.encoder import vectorize_descriptions
from database.pinecone_manager import PineconeManager
from chatbot.chatbot import (
    generate_hypothetical_description,
    get_related_courses,
    summarize_related_courses,
    chatbot,
)

# from database.pinecone_manager import PineconeManager
from data_collection.courses_scraper import (
    fetch_course_ids,
    fetch_all_course_info,
    read_course_ids,
)


def chatbot_test():
    # student_input = "I'm a STEM major, but I'm super into music and I want to take an electronic music class that doesn't shy away from the more technical aspects of production and composition. I'm also interested in cults throughout history."
    # student_input = "I'm a STEM major, but I'm super into music and I want to take a 300-level electronic music class that doesn't shy away from the more technical aspects of production and composition. I've already taken MUS205 and MUS216 so don't suggest those please."
    student_input = "I want to take an easy seminar class next semester. What suggestions do you have?"
    description = generate_hypothetical_description(student_input)
    print(f"Description: {description}")
    print("Getting related courses...")
    courses = get_related_courses(description)
    print("Got courses...")
    # print(courses)
    chatbot_response = summarize_related_courses(courses, student_input)
    print(f"chatbot response: {chatbot_response}")


async def main():
    # Step 1: Check if the course_ids.txt file exists and has content
    course_ids = read_course_ids("course_ids.txt")
    if not course_ids:
        print("Fetching new course IDs...")
        course_ids = await fetch_course_ids(
            "https://registrar.princeton.edu/course-offerings?term=1252"
        )
        # Save course_ids to file (assuming you have a utility function for this)
        with open("course_ids.txt", "w") as file:
            for course_id in course_ids:
                file.write(course_id + "\n")

    # Step 2: Fetch course descriptions
    print("Fetching course information...")
    course_info = await fetch_all_course_info(course_ids)

    # Step 3: Extract descriptions from the course information
    descriptions = {
        course_id: info["description"] for course_id, info in course_info.items()
    }
    titles = {course_id: info["titles"] for course_id, info in course_info.items()}

    print("Vectorizing descriptions...")
    vectors = vectorize_descriptions(descriptions)

    # Step 4: Initialize Pinecone and the index
    pinecone_manager = PineconeManager()
    print("Pinecone index initialized.")

    # Step 5: Upsert vectors into Pinecone in batches
    print("Upserting data into Pinecone...")
    batch_size = 5  # Define the batch size
    total_courses = len(course_ids)
    for i in range(0, total_courses, batch_size):
        batch_course_ids = course_ids[i : i + batch_size]
        items_to_upsert = [
            (
                course_id,
                vectors[course_id],
                {
                    "description": descriptions[course_id],
                    "title": titles[course_id][0],
                },  # Assuming there's at least one title
            )
            for course_id in batch_course_ids
            if course_id in vectors
        ]
        try:
            pinecone_manager.upsert(items_to_upsert)
        except:
            print(f"FAILED: {items_to_upsert}")
        print(
            f"Upserted batch {i // batch_size + 1}/{(total_courses + batch_size - 1) // batch_size}"
        )


if __name__ == "__main__":
    # asyncio.run(main())
    asyncio.run(chatbot())
    # chatbot_test()
