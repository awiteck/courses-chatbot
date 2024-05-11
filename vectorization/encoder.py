from sentence_transformers import SentenceTransformer

# Initialize the model globally to avoid reloading it each time the function is called
model = SentenceTransformer("all-MiniLM-L6-v2")


def vectorize_string(s):
    return model.encode(s)


def vectorize_descriptions(descriptions):
    """
    Encodes a dictionary of course descriptions into vectors.

    :param descriptions: A dictionary where keys are course IDs and values are descriptions
    :return: A dictionary where keys are course IDs and values are the corresponding vectors
    """
    # Ensure the model is loaded (this line is more for clarity as the model is initialized above)
    if not model:
        raise RuntimeError("Model not loaded")

    # Extract descriptions and maintain order with course_ids
    course_ids = list(descriptions.keys())
    texts = [descriptions[course_id] for course_id in course_ids]

    # Generate embeddings for each description
    vectors = model.encode(texts, show_progress_bar=True)

    # Map vectors back to course_ids
    return {course_id: vector for course_id, vector in zip(course_ids, vectors)}


# Example usage for testing directly within this script
if __name__ == "__main__":
    # Example dictionary of course IDs to descriptions
    example_descriptions = {
        "123": "Introduction to Computer Science",
        "456": "Advanced Topics in Machine Learning",
        "789": "History of Art",
    }
    encoded_vectors = vectorize_descriptions(example_descriptions)
    print(encoded_vectors)
