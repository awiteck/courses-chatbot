import asyncio
from pyppeteer import launch
from urllib.parse import urlparse, parse_qs
import os


async def fetch_course_info(course_id):
    url = f"https://registrar.princeton.edu/course-offerings/course-details?term=1252&courseid={course_id}"
    browser = await launch(headless=True)  # Headless mode means no UI
    page = await browser.newPage()
    await page.goto(url)
    await page.waitForSelector(
        "div.description"
    )  # Wait for the description div to load

    # Extract the text of the description
    description = await page.evaluate(
        """
        () => {
            const descriptionElement = document.querySelector('div.description p');
            return descriptionElement ? descriptionElement.innerText : 'No Description Found';
        }
    """
    )
    # Extract all course titles
    course_titles = await page.evaluate(
        """
        () => {
            const titlesElement = document.querySelector('div.subject-associations');
            return titlesElement ? titlesElement.innerText.trim().replace(/\s+/g, ' ').split('\\n') : [];
        }
    """
    )

    await browser.close()
    return description, course_titles


# Fetch descriptions asynchronously
async def fetch_all_course_info(course_ids):
    results = {}
    for course_id in course_ids:
        description, titles = await fetch_course_info(course_id)
        results[course_id] = {"description": description, "titles": titles}
    return results


def read_course_ids(filename):
    if not os.path.exists(filename):  # Check if the file exists
        return []  # Return an empty list if the file does not exist
    with open(filename, "r") as file:
        course_ids = [line.strip() for line in file.readlines() if line.strip()]
    return course_ids


async def fetch_course_ids(url):
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.goto(url)

    # Wait for the search button to be available and then click it
    await page.waitForSelector("#classes-search-button")
    await page.click("#classes-search-button")
    await page.waitForSelector("td.class-info")  # Wait for the initial results to load

    course_ids = []
    while True:
        print("New page...")
        # Extract all course links from the current page
        course_links = await page.evaluate(
            """
            () => Array.from(document.querySelectorAll('td.class-info a'), a => a.href)
        """
        )

        # Extract course IDs from the URLs
        for link in course_links:
            query = urlparse(link).query
            params = parse_qs(query)
            if "courseid" in params:
                course_ids.append(params["courseid"][0])

        # Use XPath to find the Next button, check if it is not the last link (disabled scenario)
        next_button = await page.xpath(
            '//div[@class="pager"]/a[contains(text(), "Next")]'
        )
        if next_button and await page.evaluate(
            '(element) => !element.classList.contains("disabled")', next_button[0]
        ):
            await next_button[0].click()
            await page.waitForSelector(
                "td.class-info", {"timeout": 10000}
            )  # Wait for new results
        else:
            break

        if len(course_links) < 100:
            break

    await browser.close()

    # Write the course IDs to a file
    with open("course_ids.txt", "w") as file:
        for course_id in course_ids:
            file.write(course_id + "\n")

    return course_ids


# course_ids = read_course_ids("course_ids.txt")
# descriptions = asyncio.run(fetch_all_descriptions(course_ids[:5]))

# # Example usage
# url = "https://registrar.princeton.edu/course-offerings?term=1252"
# course_ids = asyncio.run(fetch_course_ids(url))
# print(course_ids)

# # Example usage
# url = "https://registrar.princeton.edu/course-offerings/course-details?term=1252&courseid=015230"
# description = asyncio.run(fetch_course_description(url))
# print(description)
