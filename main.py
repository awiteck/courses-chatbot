import asyncio
from vectorization.encoder import vectorize_descriptions
from database.pinecone_manager import PineconeManager

# from database.pinecone_manager import PineconeManager
from data_collection.courses_scraper import (
    fetch_course_ids,
    fetch_all_course_info,
    read_course_ids,
)


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
    course_info = await fetch_all_course_info(course_ids[:5])

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

    # Step 5: Upsert vectors into Pinecone
    print("Upserting data into Pinecone...")
    items_to_upsert = [
        (
            course_id,
            vectors[course_id],
            {"description": descriptions[course_id], "title": titles[course_id]},
        )
        for course_id in course_ids
        if course_id in vectors
    ]
    # items_to_upsert = [(course_id, vector) for course_id, vector in vectors.items()]
    pinecone_manager.upsert(items_to_upsert)


if __name__ == "__main__":
    asyncio.run(main())
