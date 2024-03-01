import wikipedia
import openai

def wikipedia_rag(topic):

    print(topic)
    topic_summary = wikipedia.summary(topic)

    prompt = """Give a concise bullet point summary about this context

    ----
    {context}

    """.format(context=topic_summary)

    print(prompt)


if __name__ == "__main__":
    topic = input("What topic would you like to learn about? ")
    wikipedia_rag(topic)